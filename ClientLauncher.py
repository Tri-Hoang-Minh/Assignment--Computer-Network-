import sys
from tkinter import Tk
from Client import Client
from Client2 import Client2

if __name__ == "__main__":
	try:
		serverAddr = sys.argv[1]
		serverPort = sys.argv[2]
		rtpPort = sys.argv[3]
		fileName = sys.argv[4]	
	except:
		print("[Usage: ClientLauncher.py Server_name Server_port RTP_port Video_file]\n")	
	
	root = Tk()
	
	# Create a new client
	print('Normal version: 1')
	print('Extend version: 2')
	while True:
		INPUT = int(input('Choose version: '))
		if(INPUT == 1 ):
			root = Tk()
			app = Client(root, serverAddr, serverPort, rtpPort, fileName)
			break
		elif(INPUT == 2):
			root = Tk()
			app = Client2(root, serverAddr, serverPort, rtpPort, fileName)
			break

		else:
			print('Choose again:')

	app.master.title("RTPClient")	
	root.mainloop()
	