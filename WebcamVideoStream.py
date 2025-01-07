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
import numpy as np
import logging
from websockets.sync.server import serve
 
class ADSVideoStream:
	def __init__(self, resolution=(320, 240), framerate=60, wb = (1.5,1.5)):
		# initialize the camera and stream

		self.newFrame = False

		self.counter = FPSCounter(movingAverage=60).start()
		# initialize the frame and the variable used to indicate
		# if the thread should be stopped
		self.frame = None
		self.stopped = True

	def newImageCallback(self,websocket):
		self.counter.tick()
		try:
			websocket.debug = False
			for message in websocket:
				if isinstance(message,bytes):
					nparr = np.frombuffer(message,np.ubyte)
					#nparr.flags.writeable = True
					self.frame = nparr.reshape((720,1280,1))
					self.newFrame = True
		except Exception as e:
			print("WS error: "+str(e))
		#websocket.send("Pong")

	def start(self):
		if self.stopped:
			self.stopped = False
			Thread(target=self.runServer, args=()).start()
			return self
		
	def runServer(self):
		logging.getLogger("websockets").propagate = False
		with serve(self.newImageCallback, "127.0.0.1", 80,max_size=None) as server:
			server.serve_forever()

	def read(self):
		self.newFrame = False
		return self.frame
 
	def stop(self):
		self.stopped = True
		self.newFrame = False
		self.frame = None
		self.counter.stop()
		

if __name__ == "__main__":
	adsVideo = ADSVideoStream()
	repeater = Repeater(adsVideo.counter.print, 0.5).start()
