# ****************************************************************************** #
# Author: Ondrej Slama
# -------------------

# Zdrojovy kod vytvoreny v ramci projektu robotickeho vzdusneho hokeje - diplomova prace
#  na VUT FSI ustavu automatizace a informatiky v Brne.

# Source code created as a part of robotic air hockey table project - Diploma thesis
# at BUT FME institute of automation and computer sience.

# ****************************************************************************** #
# import the necessary packages
import asyncio
from threading import Thread
import websockets
import struct
import time
from pygame.math import Vector2
from UniTools import FPSCounter, Repeater
import numpy as np

class WSPositionStream:
	def __init__(self, resolution=(320, 240), framerate=60, wb=(1.5, 1.5)):
		# initialize the camera and stream
		self.newPosition = False
		self.counter = FPSCounter(movingAverage=60).start()
		self.stopped = True
		self.loop = None
		self.pos = Vector2(0,0)
		self.lastPosReceivedAt = time.time()

	async def newImageCallback(self, websocket):
		self.counter.tick()
		try:
			while True:
				data = await websocket.recv()
				if isinstance(data, bytes):
					#self.pos = Vector2(struct.unpack('dd', message))
					#self.newPosition = True
					print(1 / (time.time() - self.lastPosReceivedAt))
					self.lastPosReceivedAt = time.time()
		except Exception as e:
			print("WS error: " + str(e))

	def start(self):
		if self.stopped:
			self.stopped = False
			thread = Thread(target=self._run_event_loop, daemon=True)
			thread.start()
			return self

	def _run_event_loop(self):
		self.loop = asyncio.new_event_loop()
		asyncio.set_event_loop(self.loop)
		self.loop.run_until_complete(self.runServer())

	async def runServer(self):
		async with websockets.serve(self.newImageCallback, "", 8000, max_size=2000, compression=None):
			await asyncio.Future()  # Run the server indefinitely

	def read(self):
		self.newPosition = False
		return self.pos

	def stop(self):
		self.stopped = True
		self.newPosition = False
		self.pos = None
		if self.loop:
			self.loop.stop()
			self.loop = None
		self.counter.stop()

if __name__=="__main__":
	stream = WSPositionStream()
	stream.start()
	while True:
		time.sleep(1)