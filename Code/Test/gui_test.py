from Tkinter import *
import tkFileDialog # Get file path 
#from Record import record_audio, stop_record
import os, sys, numpy as np, pyaudio, wave


# Plot in GUI
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import librosa

	

class Application(Frame):
	
	# Record Audio
	def record_audio(self, input_device):
	
	# Open input stream
		audio_rec = pyaudio.PyAudio()
		rec_stream = audio_rec.open(
		format = pyaudio.paInt16,
		channels = 1, # mono
		rate = 44100, # sample rate of 44100 Hz
		input_device_index = input_device, # input device (mic, external, etc.)
		input = True) # Input
	
		num_samps = 1024

		self.rec_data = []
		self.rec_data_np = []
		
		self.rec_end = 0
	
		while self.rec_on is True: # Record
			rec_samps = rec_stream.read(num_samps)
			self.rec_data.append(rec_samps) # pyaudio data
			self.rec_data_np.append(np.fromstring(rec_samps, dtype=np.int16)) # pyaudio data converted to numpy
			root.update() # make sure GUI can still update & not get stuck in loop

		self.rec_data_np = np.hstack(self.rec_data_np) # output numpy data array
		librosa.output.write_wav('test_np.wav', self.rec_data_np, 44100, norm=False)
		print len(self.rec_data_np)
	# Close Stream
		rec_stream.stop_stream()
		rec_stream.close()
		audio_rec.terminate()
		
		self.rec_end = 1

		waveFile = wave.open("test_rec.wav", 'wb')
		waveFile.setnchannels(1)
		waveFile.setsampwidth(audio_rec.get_sample_size(pyaudio.paInt16))
		waveFile.setframerate(44100)
		waveFile.writeframes(b''.join(self.rec_data))
		waveFile.close()
		
	
	# Get File Path for WAV File
	def wav_file_path(self):
		self.wave_path = tkFileDialog.askopenfilename()
		self.wptext.delete('1.0', END)
		self.wptext.insert(INSERT,self.wave_path)
		self.play_rec["state"] = NORMAL
		
	# Run Aubio Demo
	def run_pitch_track(self):
		sr = self.sr_entry.get()
		sr = int(float(sr))
		os.system('python test_aubio.py %s %d' % (self.wave_path,sr))

	# Run InstruSwitch
#	def run_instruswitch(self):
		
	
	# Input Select		
	def rb_select(self):
		rb_sel =  rbvar.get()
		if rb_sel is 1: # File Upload Selected
			self.record_button["state"] = DISABLED
			self.sr_entry["state"] = NORMAL
			self.wpath["state"] = NORMAL
			self.input_mb["state"] = DISABLED
		if rb_sel is 2: # Record Selected
			self.record_button["state"] = NORMAL
			self.sr_entry["state"] = DISABLED
			self.wpath["state"] = DISABLED
			self.input_mb["state"] = NORMAL
			
	# Record
	def record_start(self):
		mb_sel =  mbvar.get()
		if mb_sel == 1: # Mic as Input
			self.rec_on = True
			print "Recording..."
			self.record_audio(0)
		#if mb_sel == 2: # External as Input
		#	Rec_on = True
		#	print "Recording..."
		#	record_audio(1)
		
	# Stop
	def stop_rec_play(self):
		if self.rec_on is True:
			self.rec_on = False
			print "Finished Recording"
			self.play_rec["state"] = NORMAL
			self.save_rec["state"] = NORMAL
			rb_sel =  rbvar.get()
			#while self.rec_end is 0: pass
	
				
		#if play_on is True:
	
	#def save_file(self):
	
	def plot_input(self):
		fig1 = Figure(figsize=(5,5), dpi=100)
		a1 = fig1.add_subplot(111)
		rb_sel =  rbvar.get()
		if rb_sel is 1:
			1
		if rb_sel is 2:
			t_length = len(self.rec_data_np)
			times = np.arange(0,t_length * 44100)/44100.
			print len(self.rec_data_np), times.shape
			a1.plot(times, self.rec_data_np)
			#input_fig = FigureCanvasTkAgg(fig1, self)
			#input_fig.show()
			#input_fig.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)

			#input_fig_toolbar = NavigationToolbar2TkAgg(input_fig, self)
			#input_fig_toolbar.update()
			#input_fig._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)

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
		self.record_button["command"] = self.record_start
		self.record_button["activeforeground"] = "red"
		self.record_button.pack({"side": "left"})
		
		# Stop Button
		self.stop_button = Button(self, text="Stop", command=self.stop_rec_play)
		self.stop_button.pack({"side": "left"})
		
		# Run Button
		self.run_button = Button(self, text="Run", command=self.run_pitch_track)
		self.run_button.pack({"side": "left"})
		
		# WAV File Load Button
		self.wpath = Button(self, text="Load WAV File",command=self.wav_file_path)
		self.wpath.pack({"side": "left"})
		self.wptext = Text(self, height=1, width=40)
		self.wptext.insert(INSERT, "WAV Path")
		self.wptext.pack({"side": "left"})
	
		# Sample Rate Entry
		self.sr_label = Label(self, text="Sample Rate (Hz)").pack({"side": "left"})
		self.sr_entry = Entry(self)
		self.sr_entry.insert(0, 44100)
		self.sr_entry.pack({"side": "left"})
		
		# Input Selections		
		global mbvar
		mbvar = IntVar()
		self.input_mb = Menubutton(self, text="Select Input")
		self.input_mb.grid()
		self.input_mb.menu = Menu(self.input_mb, tearoff=0)
		self.input_mb["menu"]  =  self.input_mb.menu
		self.input_mb.menu.add_radiobutton(label="Mic", variable=mbvar, value=1)
		self.input_mb.menu.add_radiobutton(label="External Instrument", variable=mbvar, value=2)
		
		global rbvar
		rbvar = IntVar()
		self.file_rb = Radiobutton(self, text="File Upload", variable=rbvar, value=1, command=self.rb_select)
		self.file_rb.pack(anchor = NW)
		self.file_rb.invoke()
		self.record_rb = Radiobutton(self, text="Record", variable=rbvar, value=2, command=self.rb_select)
		self.record_rb.pack(anchor = NW)
		#self.live_rb = Radiobutton(self, text="Live", variable=var, value=3)
		
		self.input_mb.pack({"side": "left"})
		
		# Save Buttons
		self.save_label = Label(self, text="Save Path").pack({"side": "left"})
		self.save_entry = Entry(self)
		self.save_entry.pack({"side": "left"})
		
		self.save_rec = Button(self, text="Save Recorded Audio", state=DISABLED)
		self.save_rec.pack({"side": "left"})
		
		self.save_out = Button(self, text="Save Output", state=DISABLED)
		self.save_out.pack({"side": "left"})
		
		# Play Button
		self.play_rec = Button(self, text="Play Recording", state=DISABLED)
		self.play_rec.pack({"side": "left"})
		self.play_out = Button(self, text="Play Output", state=DISABLED)
		self.play_out.pack({"side": "left"})
		

		
		
		
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.pack()
		self.createWidgets()

		

root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()