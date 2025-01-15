# ****************************************************************************** #
# Author: Ondrej Slama
# -------------------

# Zdrojovy kod vytvoreny v ramci projektu robotickeho vzdusneho hokeje - diplomova prace
#  na VUT FSI ustavu automatizace a informatiky v Brne.

# Source code created as a part of robotic air hockey table project - Diploma thesis
# at BUT FME institute of automation and computer sience.

# ****************************************************************************** #
# import the necessary packages
from threading import Thread
from UniTools import FPSCounter, Repeater
import cv2
import time
import pyads
import Constants
from pygame import Vector2
import numpy as np
import asyncio
from websockets.asyncio.server import serve
from ctypes import sizeof
 
class ADSVideoStream:
	def __init__(self, resolution=(320, 240), framerate=60, wb = (1.5,1.5)):
		# initialize the camera and stream
		self.plc = pyads.Connection("5.132.128.125.1.1", 856,"169.254.190.31")
		self.plc.open();
		self.tags = {
			"GVL_ADS_PythonBridge.aPuckWorldPosition":pyads.PLCTYPE_ARR_LREAL(2)
			,"GVL_ADS_PythonBridge.aCurrentStrikerPosition":pyads.PLCTYPE_ARR_LREAL(2)
			}

		self.newPuckPosition = False
		self.newStrikerPosition = False

		self.counter = FPSCounter(movingAverage=60).start()

		# initialize the frame and the variable used to indicate
		# if the thread should be stopped
		self.puckPos = None
		self.strikerPos = None
		self.stopped = True

	def start(self):
		if self.stopped:
			self.stopped = False
			attr = pyads.NotificationAttrib(sizeof(pyads.PLCTYPE_ARR_LREAL(2)))
			self.handles = self.plc.add_device_notification("GVL_ADS_PythonBridge.aPuckWorldPosition",attr,self.newImageCallback)
			self.handles = self.plc.add_device_notification("GVL_ADS_PythonBridge.aCurrentStrikerPosition",attr,self.newStrikerPosCallback)
			return self
		
	def newStrikerPosCallback(self,notification,data):
		self.strikerPos = Vector2(self.plc.parse_notification(notification,pyads.PLCTYPE_ARR_LREAL(2))[2])
		self.newStrikerPosition = True
		
	def newImageCallback(self,notification,data):
		start_time = time.perf_counter()
		self.counter.tick()
		self.puckPos = Vector2(self.plc.parse_notification(notification,pyads.PLCTYPE_ARR_LREAL(2))[2])
		self.newPuckPosition = True
		end_time = time.perf_counter()
		elapsed_time = end_time - start_time
		#print(f"Function execution time: {elapsed_time:.6f} seconds")

	def read(self):
		
		# bufferContent = self.plc.read_by_name("GVL_ImageAnalysisTransfer.aImageBuffer",pyads.PLCTYPE_BYTE*921600);

		# nparr = np.frombuffer(bytes(bufferContent),np.ubyte)
		# #nparr.flags.writeable = True
		# self.pos = nparr.reshape((720,1280,1))

		
		# return the frame most recently read
		self.newPuckPosition = False

		#transform position to fit piHockeys coordinate-system ((0,0) right in front of robot's goal)
		self.puckPos.y -= Constants.FIELD_HEIGHT/2
		self.puckPos.y *= -1
		return self.puckPos
	
	def getStrikerPos(self):
		x=self.strikerPos.y
		y=self.strikerPos.x

		y-=int(Constants.FIELD_HEIGHT/2)
		y*=-1

		self.newStrikerPosition = False

		return Vector2(x,y)
	
	def write(self,pos):
		x = -pos[1]
		y = pos[0]
		x += int(Constants.FIELD_HEIGHT/2)
		self.plc.write_by_name("GVL_ADS_PythonBridge.aDesiredStrikerPosition",(x,y),pyads.PLCTYPE_ARR_INT(2))
 
	def stop(self):
		self.plc.del_device_notification(self.handles)
		self.plc.close()
		self.stopped = True
		self.newFrame = False
		self.puckPos = None
		self.counter.stop()
		

if __name__ == "__main__":
	pass

	adsVideo = ADSVideoStream()
	adsVideo.start()

	repeater = Repeater(adsVideo.counter.print, 0.5).start()
