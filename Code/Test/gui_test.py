from Tkinter import *
import tkFileDialog # Get file path 

import os, sys

# Plot in GUI
#import matplotlib
#matplotlib.use("TkAgg")
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
#from matplotlib.figure import Figure

class Application(Frame):
	def record_text(self):
		print "Recording..."
		
	# Get File Path for WAV File
	def wav_file_path(self):
		global wave_path
		wave_path = tkFileDialog.askopenfilename()
		self.wptext.delete('1.0', END)
		self.wptext.insert(INSERT,wave_path)
		
	# Run Aubio Demo
	def run_pitch_track(self):
		global sr
		sr = self.sr_entry.get()
		sr = int(float(sr))
		os.system('python test_aubio.py %s %d' % (wave_path,sr))

	def createWidgets(self): # Create Widgets
		# QUIT Button
		self.QUIT = Button(self)
		self.QUIT["text"] = "QUIT"
		self.QUIT["fg"]   = "red"
		self.QUIT["command"] =  self.quit
		self.QUIT.pack({"side": "left"})
		
		# Record Button
		self.record_button = Button(self)
		self.record_button["text"] = "Record",
		self.record_button["command"] = self.record_text
		self.record_button["activeforeground"] = "red"
		self.record_button.pack({"side": "left"})
		
		# Stop Button
		self.stop_button = Button(self, text="Stop").pack({"side": "left"})
		
		# Run Button
		self.run_button = Button(self, text="Run", command=self.run_pitch_track).pack({"side": "left"})
		
		# WAV File Load Button
		self.wpath = Button(self, text="Load WAV File",command=self.wav_file_path).pack({"side": "left"})
		self.wptext = Text(self, height=1, width=40)
		self.wptext.insert(INSERT, "WAV Path")
		self.wptext.pack({"side": "left"})
	
		# Sample Rate Entry
		self.sr_label = Label(self, text="Sample Rate (Hz)").pack({"side": "left"})
		self.sr_entry = Entry(self)
		self.sr_entry.insert(0, 44100)
		self.sr_entry.pack({"side": "left"})
		
		
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.pack()
		self.createWidgets()

root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()