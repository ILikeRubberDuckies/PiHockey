import serial
import time
from HelperClasses import FPSCounter
from threading import Thread

class Serial():
	def __init__(self, settings):
		self.settings = settings
		# Reading ----
		self.vectors = [(0,0), (0,0)]
		self.status = None

		self._readingLine = ""
		self._writingLine = "ahoj"

		self._prevWrite = ""

		self._baudRate = 115200
		self._readingCounter = FPSCounter(60)
		self._writingCounter = FPSCounter(60)
		self._ser = None

		self._stopped = True
		self._lastRead = 0
		self._lastWrite = 0

	def readStatus(self):
		output = self.status
		self.status = None
		return output	

	def writeLine(self, txt, *args):
		self._writingLine = txt
	
	def writeVector(self, vector, mode):
		self.writeLine("{},{},{}".format(mode,*[*vector].copy()))

	def _reading(self):
		_prevTime = time.time()
		_num = 0
		while True:
			self._lastRead = time.time() 	
			self._readingCounter.tick()
			try:
				self._readingLine = self._ser.readline().decode('utf-8').rstrip()
				#print(self._readingLine)
				self._parseReading(self._readingLine)
				_num += 1
				if time.time() - _prevTime > 1:
					_prevTime = time.time()
					# print(_num)python

					_num = 0

			except:
				print("Error while decoding")
				
			sleepTime = 1/self.settings["communicationFrequency"] - (time.time() - self._lastRead)
			if sleepTime > 0:
				time.sleep(sleepTime)

			if self._stopped:				
				return

	def _writing(self):
		while True:
			self._lastWrite = time.time()
			#print(time.time())
			if not self._writingLine == self._prevWrite and not self._writingLine == "":
				self._writingCounter.tick()
				self._prevWrite = self._writingLine			
				self._ser.write((str(self._writingLine) + '\n').encode('ascii'))
				#print((str(self._writingLine) + '\n'))
			sleepTime = 1/self.settings["communicationFrequency"] - (time.time() - self._lastWrite)
			if sleepTime > 0:
				time.sleep(sleepTime)

			if self._stopped:				
				return

	def _parseReading(self, txt):
		if txt == "e1" or txt == "e2" or txt == "e3": 
			self.status = txt
		else:
			try:
				# print(txt.split(",")[1:3])
				# [print(x) for x in txt.split(",")[1:3]]				
				i = 0
				parse = []
				for vector in txt.split(";"):
					for x in vector.split(","):
						try:
							parse.append(round(float(x)))
						except: pass
						# parse = [round(float(x)) for x in txt.split(",")[1:3]]
						
					self.vectors[i] = (parse[0], parse[1])
					i += 1

			except Exception as e: 
				# print(e)
				pass
				# print("Could not parse reading.")
							     

	def start(self):
		if self._stopped:
			# self._ser = serial.Serial('/dev/ttyACM0', self._baudRate, )	
			self._ser = serial.Serial('/dev/ttyUSB0', self._baudRate)	
			self._ser.flush()
			self._readingCounter.start()
			self._writingCounter.start()
			self._stopped = False
			Thread(target=self._reading, args=()).start()
			Thread(target=self._writing, args=()).start()
			print("Communication started.")
		return self

	def stop(self):
		self._readingCounter.stop()
		self._writingCounter.stop()
		self._ser = None
		self._stopped = True
		print("Communication _stopped.")

if __name__ == '__main__':
	serial = Serial().start()
	serial._readingCounter.schedulePrint(0.5, "Reading:")
	serial._writingCounter.schedulePrint(0.5, "Writing:")

	while True:
		serial.writeLine(input())
        
