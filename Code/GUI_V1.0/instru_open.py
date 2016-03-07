from Tkinter import *
import tkFileDialog # Get file path 
#from Record import record_audio, stop_record
import os, sys, numpy as np, pyaudio, wave, tkFont
#from PIL import Image, ImageTk


# Plot in GUI

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure


import librosa

	

class Application(Frame):
	def run_program(self):
		self.instru_open["state"] = DISABLED
		root.after(500, self.instru_run)
		
	def instru_run(self):
		os.system('python gui_test.py')
		self.quit()
		
	
		# Create Widgets
	def createWidgets(self): 
		# QUIT Button
		ti_sw = PhotoImage(file="instru_switch_switch.gif")
		ti_sw = ti_sw.subsample(6,6)
		self.instru_open = Button(self)
		self.instru_open["image"] = ti_sw
		self.instru_open.image = ti_sw
		self.instru_open["command"] =  self.run_program
		self.instru_open.grid(row=0, column=0, sticky=NW)
	

		
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.pack()
		self.createWidgets()

		

root = Tk()
app = Application(master=root)
app.configure(bg="grey85")
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
x = w/2 - 70/2
y = h/2 - 90/2
root.geometry("%dx%d+%d+%d" % (70,90,x, y))
root.lift()
root.attributes("-topmost", True)
root.attributes("-topmost", False)
app.mainloop()
root.destroy()