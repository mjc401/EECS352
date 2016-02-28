from Tkinter import *
import tkFileDialog # Get file path 

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
		
		# WAV File Load Button
		self.wpath = Button(self, text="Load WAV File",command=self.wav_file_path).pack({"side": "left"})
	
		
		
		
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.pack()
		self.createWidgets()

root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()