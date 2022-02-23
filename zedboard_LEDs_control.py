from tkinter import *
import tkinter.ttk
import serial
from configparser import ConfigParser
import os
import platform
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import sys

UP_COMMAND =        0x75
DOWN_COMMAND =      0x64
PAUSE_COMMAND =     0x20
LEFT_COMMAND =      0x6C
RIGHT_COMMAND =     0x72
READ_ADC_COMMAND =  0x88



class App:
	def __init__(self):
		self.root = Tk()
		self.root.grid_columnconfigure(0,weight=1)
		self.root.grid_rowconfigure(0,weight=1)

		self.mainPanel = Frame(self.root)
		self.mainPanel.grid(row=0,column=0)
		self.mainPanel.columnconfigure(0,weight=1)
		self.mainPanel.rowconfigure(0,weight=1)

		#---------------------------------------------------------------------------------
		# mimick zedboard pushbuttons
		self.button_up = Button(self.mainPanel,command=self.sendUp,text="Faster",
								height=1,width=20).grid(row=0,column=1)
		self.button_center = Button(self.mainPanel,command=self.sendPause,text="Pause",
								height=1,width=20).grid(row=1,column=1)
		self.button_down = Button(self.mainPanel,command=self.sendDown,text="Slower",
								height=1,width=20).grid(row=2,column=1)
		self.button_right = Button(self.mainPanel,command=self.sendRight,text="Right",
								height=1,width=20).grid(row=1,column=2)
		self.button_left = Button(self.mainPanel,command=self.sendLeft,text="Left",
								height=1,width=20).grid(row=1,column=0,sticky='e')
    	#---------------------------------------------------------------------------------


		tkinter.ttk.Separator(self.mainPanel,orient='horizontal').grid(row=3,column=0,columnspan=3,
																pady=15,sticky='ew')


        #---------------------------------------------------------------------------------
		self.button_loadSawtoothUp = Button(self.mainPanel,command=self.loadSawtoothUp,text="Load Sawtooth Up",
									height=1,width=20).grid(row=4,column=1)
		self.button_loadSawtoothDown = Button(self.mainPanel,command=self.loadSawtoothDown,text="Load Sawtooth Down",
									height=1,width=20).grid(row=5,column=1)
		self.button_getData = Button(self.mainPanel,command=self.getData,text="Get Data",
									height=1,width=20).grid(row=6,column=1)

		self.numDataPoints = IntVar()
		Entry(self.mainPanel,width=5,textvariable=self.numDataPoints).grid(row=6,column=2,sticky='w',padx=5)
		self.numDataPoints.set(1000)

		self.button_flushInput = Button(self.mainPanel,command=self.FlushInput,text="Flush Input",
									height=1,width=20).grid(row=7,column=1)
        #---------------------------------------------------------------------------------


		self.dataPoints = [1,2,3,4]
		self.update_plot()

        #---------------------------------------------------------------------------------
		self.dataPoints = [1,2,3,4]
		self.fig = Figure(figsize=(5,2), dpi=100)
		self.fig.suptitle("Returned Data")
		self.ax = self.fig.add_subplot(111)
		self.t_line, = self.ax.plot(self.dataPoints)
		canvas = FigureCanvasTkAgg(self.fig,self.mainPanel)
		canvas.draw()
		canvas.get_tk_widget().grid(row=8,column=0,columnspan=5)

        #---------------------------------------------------------------------------------

		self.read_config_file()
		self.initSerialPort()

		self.root.protocol("WM_DELETE_WINDOW", self.onExit)
		self.root.title("Zedboard Control")
		self.root.geometry('650x450')
		self.root.mainloop()

	def update_plot(self):
		self.fig = Figure(figsize=(5,2), dpi=100)
		self.fig.suptitle("Returned Data")
		self.ax = self.fig.add_subplot(111)
		self.t_line, = self.ax.plot(self.dataPoints)
		canvas = FigureCanvasTkAgg(self.fig,self.mainPanel)
		canvas.draw()
		canvas.get_tk_widget().grid(row=8,column=0,columnspan=5,pady=10)

	def read_config_file(self):

		config_file_name = "settings.cfg"
		cwd = os.getcwd()
		c_file = open(cwd + '/config/' + config_file_name)

		config_file = ConfigParser()
		config_file.read_file(c_file)

		if platform.system() == 'Windows':
			self.COMport = config_file.get('Port Settings','win_COM_port')
		else:
			self.COMport = config_file.get('Port Settings','linux_COM_port')

		self.baudRate = int(config_file.get('Port Settings','baud_rate'))
		self.timeoutSec = int(config_file.get('Port Settings','timeoutSec'))


	def initSerialPort(self):
		self.port = serial.Serial(self.COMport, self.baudRate, timeout=self.timeoutSec)

	def sendUp(self):
		#send 0x75 for UP command
		self.port.write(bytearray([UP_COMMAND]))

	def sendDown(self):
		#send 0x64 for DOWN command
		self.port.write(bytearray([DOWN_COMMAND]))

	def sendPause(self):
		#send 0x20 for PAUSE command
		self.port.write(bytearray([PAUSE_COMMAND]))

	def sendLeft(self):
		#send 0x6C for LEFT command
		self.port.write(bytearray([LEFT_COMMAND]))

	def sendRight(self):
		#send 0x72 for RIGHT command
		self.port.write(bytearray([RIGHT_COMMAND]))

	def loadSawtoothUp(self):
		print("Loading Sawtooth Up")
		#send 0x62 for loading sawtooth_up waveform data
		self.port.write(chr(0x62))

	def loadSawtoothDown(self):
		print("Loading Sawtooth Down")
		#send 0x63 for loading sawtooth_down waveform data
		self.port.write(chr(0x63))

	def getData(self):
		print("flushing data at input...")
		self.port.flushInput()

		#the zedboard command for reading data
		cmd = 0x61

		numPoints = self.numDataPoints.get()
		numberByte1 = numPoints >> 8
		numberByte2 = numPoints & 0xFF

		print("Getting Data (%d values)")
		self.port.write(bytearray([cmd,numberByte1,numberByte2]))

		#read expected number of data points from uart
		uartString=self.port.read(numPoints)

		retData = []
		for _byte in uartString:
			retData.append(ord(_byte))

		print(("number of bytes returned : %d"%(len(uartString))))
		print(("number of bytes converted: %d"%(len(retData))))

		if len(retData) > 0:
			self.dataPoints = retData
			self.ax.clear()
			self.update_plot()

		numToPrint = 15
		print(("printing first %d values..."%(numToPrint)))
		for i in range(numToPrint):
			print(("  %d: %s"%(i,retData[i])))

	def FlushInput(self):
		print("flushing input...")
		self.port.flushInput()
		print(self.numDataPoints.get())
		print("done")

	def onExit(self):
		self.root.destroy()
		sys.exit()

app = App()