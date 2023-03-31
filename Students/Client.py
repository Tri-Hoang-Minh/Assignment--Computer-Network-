from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os
import time

from RtpPacket import RtpPacket

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"
FORMAT = 'utf-8'

class Client:
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT
	
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3
	
	connectRTSP = False
	counter = 0
	# Initiation..
	def __init__(self, master, serveraddr, serverport, rtpport, filename):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.createWidgets()
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.rtpPort = int(rtpport)
		self.fileName = filename
		self.rtspSeq = 0
		self.sessionId = 0
		self.requestSent = -1
		self.teardownAcked = 0
		self.connectToServer()
		self.frameNbr = 0
		self.counter = 0
		
	# THIS GUI IS JUST FOR REFERENCE ONLY, STUDENTS HAVE TO CREATE THEIR OWN GUI 	
	def createWidgets(self):
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3)
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupMovie
		self.setup.grid(row=1, column=0, padx=2, pady=2)
		
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playMovie
		self.start.grid(row=1, column=1, padx=2, pady=2)
		
		# Create Pause button			
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=1, column=2, padx=2, pady=2)
		
		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=1, column=3, padx=2, pady=2)
		
		# Create a label to display the movie
		self.label = Label(self.master, height=19)
		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
	
	def resetAttribute(self):
		for i in os.listdir():
			if i.find(CACHE_FILE_NAME) == 0:
				os.remove(i)
		time.sleep(1)
		self.rtspSeq = 0
		self.sessionId = 0
		self.requestSent = -1
		self.teardownAcked = 0
		self.connectToServer()
		self.frameNbr = 0
		self.connectRTSP = False
		self.counter = 0
		

	def setupMovie(self):
		"""Setup button handler."""
		if self.state == self.INIT:
			if self.teardownAcked == 1:
				self.resetAttribute()
			self.sendRtspRequest(self.SETUP)
	
	def exitClient(self):
		"""Teardown button handler."""
		if self.state == self.PLAYING or self.state == self.READY:
			self.sendRtspRequest(self.TEARDOWN)
			self.label.pack_forget()
			self.label.image = ''
			 # os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT)

	def pauseMovie(self):
		"""Pause button handler."""
		if self.state == self.PLAYING:
			self.sendRtspRequest(self.PAUSE)
	
	def playMovie(self):
		"""Play button handler."""
		if self.state == self.READY:
			self.sendRtspRequest(self.PLAY)
			self.thread_listenRTP = threading.Thread(target=self.listenRtp)
			self.exit_thread_listenRTP = threading.Event()
	
	def listenRtp(self):
		"""Listen for RTP packets."""
		while True:
			try:
				data = self.rtpSocket.recv(20480) # -> đọc tối đa 20480 bytes
				if data:
					rtpPacket = RtpPacket()
					rtpPacket.decode(data) # giải mã data
					
					currFrameNbr = rtpPacket.seqNum()
					print("Current Seq Num: " + str(currFrameNbr))

					try:
						print(self.frameNbr +1,'--',rtpPacket.seqNum())
						if self.frameNbr + 1 != rtpPacket.seqNum():
							self.counter += 1 #flag khi mất gói tin
							print('!' * 60 + "\nPACKET LOSS\n" + '!' * 60)
						currFrameNbr = rtpPacket.seqNum() # gán làm qq gì ?
					# version = rtpPacket.version()
					except:
						print("seqNum() Loi \n")
						traceback.print_exc(file=sys.stdout)
						print("\n")
					if currFrameNbr > self.frameNbr: # Discard the late packet
						self.frameNbr = currFrameNbr
						self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
			except:
				# Stop listening upon requesting PAUSE or TEARDOWN
				if self.exit_thread_listenRTP.isSet(): 
					break

	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
		cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
		file = open(cachename, "wb")
		file.write(data)
		file.close()
		
		return cachename
	
	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
		    # Open image file and convert to ImageTk format
		image = Image.open(imageFile)
		photo = ImageTk.PhotoImage(image)
		
		# Update label widget with new image
		self.label.config(image=photo,height=288)
		self.label.image = photo
		
	def connectToServer(self):
		"""Connect to the Server. Start a new RTSP/TCP session."""
		self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.rtspSocket.connect((self.serverAddr, self.serverPort))
		except:
			tkinter.messagebox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' %self.serverAddr)
	
	
	def sendRtspRequest(self, requestCode):
		"""Send RTSP request to the server."""	
		#-------------
		# TO COMPLETE
		#-------------
		if requestCode == self.SETUP:
			self.connectRTSP = True
			threading.Thread(target=self.recvRtspReply).start()
			# Update RTSP sequence number.
			# ...
			self.rtspSeq = self.rtspSeq + 1
			# Write the RTSP request to be sent.
			# request = ...
			request = "SETUP %s RTSP/1.0\nCSeq: %d\nTRANSPORT: RTP/UDP; client_port= %d" % (self.fileName, self.rtspSeq, self.rtpPort)

			# Keep track of the sent request.
			# self.requestSent = ...
			self.requestSent = self.SETUP
		elif requestCode == self.PLAY:
			# Update RTSP sequence number.
			# ...
			self.rtspSeq = self.rtspSeq + 1
			# Write the RTSP request to be sent.
			# request = ...
			request = "PLAY %s RTSP/1.0\nCSeq: %d\nSESSION: %d" % (self.fileName, self.rtspSeq, self.sessionId)

			# Keep track of the sent request.
			# self.requestSent = ...
			self.requestSent = self.PLAY
		elif requestCode == self.PAUSE:
			# Update RTSP sequence number.
			# ...
			self.rtspSeq = self.rtspSeq + 1
			# Write the RTSP request to be sent.
			# request = ...
			request = "PAUSE %s RTSP/1.0\nCSeq: %d\nSESSION: %d" % (self.fileName, self.rtspSeq, self.sessionId)

			# Keep track of the sent request.
			# self.requestSent = ...
			self.requestSent = self.PAUSE
		elif requestCode == self.TEARDOWN:
			# Update RTSP sequence number.
			# ...
			self.rtspSeq = self.rtspSeq + 1
			# Write the RTSP request to be sent.
			# request = ...
			request = "TEARDOWN %s RTSP/1.0\nCSeq: %d\nSESSION: %d" % (self.fileName, self.rtspSeq, self.sessionId)
			
			# Keep track of the sent request.
			# self.requestSent = ...
			self.requestSent = self.TEARDOWN

		self.rtspSocket.send(request.encode(FORMAT))
	
	def recvRtspReply(self):
		"""Receive RTSP reply from the server."""
		while self.connectRTSP:
			reply = self.rtspSocket.recv(1024)
			if reply:
				print("Data received:\n" + reply.decode("utf-8"))
				self.parseRtspReply(reply.decode("utf-8"))

	
	def parseRtspReply(self, data):
		"""Parse the RTSP reply from the server."""
		reply = data.split('\n')
		
		# Get code
		code = int((reply[0].split(' '))[1])

		# Get the RTSP sequence number 
		seq = int((reply[1].split(' '))[1])

		# Get session 
		session = int((reply[2].split(' '))[1])

		if code == 200 and self.rtspSeq == seq:
			if self.sessionId == 0:
				# new RTSP session ID
				self.sessionId = session
			if self.sessionId == session:
				if self.requestSent == self.SETUP:
					# change state
					self.state = self.READY
					# Open RTP Port
					self.openRtpPort()

				elif self.requestSent == self.PLAY:
					# change state
					self.state = self.PLAYING
					# begin thread for listenRTP
					self.thread_listenRTP.start()

				elif self.requestSent == self.PAUSE:
					# change state
					self.state = self.READY
					# stop thread listen RTP
					self.exit_thread_listenRTP.set()

				elif self.requestSent == self.TEARDOWN:
					# change state
					self.state = self.INIT
					# Flag the teardownAcked to close the socket.
					self.teardownAcked = 1
					# terminate rtsp socket and while loop for receive RTSP socket from sever
					self.connectRTSP = False
					self.rtspSocket.shutdown(socket.SHUT_RDWR)
					self.rtspSocket.close()
					# terminate rtp socket and while loop for receive RTP socket from sever
					self.exit_thread_listenRTP.set()
					self.rtpSocket.shutdown(socket.SHUT_RDWR)
					self.rtpSocket.close()
					# delete cache file 
					os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT)


	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		#-------------
		# TO COMPLETE
		#-------------
		# Create a new datagram socket to receive RTP packets from the server
		# self.rtpSocket = ...
		self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# Set the timeout value of the socket to 0.5sec
		# ...
		self.rtpSocket.settimeout(0.5)
		try:
			# Bind the socket to the address using the RTP port given by the client user
			# ...
			self.rtpSocket.bind(('', self.rtpPort))
		except:
			tkinter.messagebox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' %self.rtpPort) 


	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		if self.state == self.PLAYING:
			self.pauseMovie()
		try:
			self.exitClient() # Close the client socket
		except:
			pass
		self.master.destroy() # Close the GUI