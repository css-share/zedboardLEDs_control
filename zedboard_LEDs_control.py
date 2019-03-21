from Tkinter import *
import ttk
import serial
from ConfigParser import ConfigParser
import os
import platform


class App:
	def __init__(self):
		self.root = Tk()
		self.root.grid_columnconfigure(0,weight=1)
		self.root.grid_rowconfigure(0,weight=1)

		self.mainPanel = Frame(self.root)
		self.mainPanel.grid(row=0,column=0)
		self.mainPanel.columnconfigure(0,weight=1)
		self.mainPanel.rowconfigure(0,weight=1)

		self.button_up = Button(self.mainPanel,command=self.sendUp,text="Faster",
								height=1,width=20).grid(row=0,column=1)
		self.button_center = Button(self.mainPanel,command=self.sendPause,text="Pause",
								height=1,width=20).grid(row=1,column=1)
		self.button_down = Button(self.mainPanel,command=self.sendDown,text="Slower",
								height=1,width=20).grid(row=2,column=1)
		self.button_right = Button(self.mainPanel,command=self.sendRight,text="Right",
								height=1,width=20).grid(row=1,column=2)
		self.button_left = Button(self.mainPanel,command=self.sendLeft,text="Left",
								height=1,width=20).grid(row=1,column=0)

		self.read_config_file()
		self.initSerialPort()

		self.root.protocol("WM_DELETE_WINDOW", self.onExit)
		self.root.title("Zedboard Control")
		self.root.geometry('500x200')
		self.root.mainloop()


	def read_config_file(self):

		config_file_name = "settings.cfg"
		cwd = os.getcwd()
		c_file = open(cwd + '/config/' + config_file_name)

		config_file = ConfigParser()
		config_file.readfp(c_file)

		if platform.system() == 'Windows':
			self.COMport = int(config_file.get('Port Settings','win_COM_port'))-1
		else:
			self.COMport = config_file.get('Port Settings','linux_COM_port')

		self.baudRate = int(config_file.get('Port Settings','baud_rate'))
		self.timeoutSec = int(config_file.get('Port Settings','timeoutSec'))


	def initSerialPort(self):
		self.port = serial.Serial(self.COMport, self.baudRate, timeout=self.timeoutSec)

	def sendUp(self):
		#send 0x75 for UP command
		self.port.write(chr(0x75))

	def sendDown(self):
		#send 0x64 for DOWN command
		self.port.write(chr(0x64))

	def sendPause(self):
		#send 0x20 for PAUSE command
		self.port.write(chr(0x20))

	def sendLeft(self):
		#send 0x6C for LEFT command
		self.port.write(chr(0x6C))

	def sendRight(self):
		#send 0x72 for RIGHT command
		self.port.write(chr(0x72))

	def onExit(self):
		self.root.quit()

app = App()