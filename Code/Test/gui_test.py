from Tkinter import *
import tkFileDialog # Get file path 
#from Record import record_audio, stop_record
import os, sys, numpy as np, pyaudio, wave, tkFont


# Plot in GUI
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import librosa

	

class Application(Frame):
	
# AUDIO (RECORD, PLAY, LIVE)
	# Record Audio
	def record_audio(self, input_device):
	
		# Open input stream
		self.audio_rec = pyaudio.PyAudio()
		rec_stream = self.audio_rec.open(
		format = pyaudio.paInt16,
		channels = 1, # mono
		rate = 44100, # sample rate of 44100 Hz
		input_device_index = input_device, # input device (mic, external, etc.)
		input = True) # Input
	
		num_samps = 1024

		self.rec_data = []
		self.rec_data_np = []
	
		while self.rec_on is True: # Record
			rec_samps = rec_stream.read(num_samps)
			self.rec_data.append(rec_samps) # pyaudio data
			self.rec_data_np.append(np.fromstring(rec_samps, dtype=np.int16)) # pyaudio data converted to numpy
			root.update() # make sure GUI can still update & not get stuck in loop

		self.rec_data_np = np.hstack(self.rec_data_np) # output numpy data array
		#librosa.output.write_wav('test_np.wav', self.rec_data_np, 44100, norm=False)

		# Close Stream
		rec_stream.stop_stream()
		rec_stream.close()
		self.audio_rec.terminate()
		
	# Play Audio
	def play_audio(self):
		self.audio_sel =  self.playbvar.get()
		if self.audio_sel is 1: # Play Original
			if self.rb_sel is 1: # From File Upload
				wav_play = wave.open(self.wave_path, 'rb')

				p_aud = pyaudio.PyAudio()

				play_stream = p_aud.open(format=p_aud.get_format_from_width(wav_play.getsampwidth()),
				channels=wav_play.getnchannels(),
				rate=wav_play.getframerate(),
				output=True)

				play_data = wav_play.readframes(1024)
				self.play_on = True

				while play_data != '' and self.play_on is True:
					play_stream.write(play_data)
					play_data = wav_play.readframes(1024)
					root.update()

				play_stream.stop_stream()
				play_stream.close()
	
				p_aud.terminate()
				
			if self.rb_sel is 2: # From Recording
				p_aud = pyaudio.PyAudio()

				play_stream = p_aud.open(
				format=pyaudio.paInt16,
				channels=1,
				rate=44100,
				output=True)
				
				self.play_on = True
				i = 1
				play_data = self.rec_data_np[0:1023].astype(np.int16).tostring()

				while play_data != '' and self.play_on is True:
					play_stream.write(play_data)
					start = i*1023
					end = start + 1023
					play_data = self.rec_data_np[start:end].astype(np.int16).tostring()
					i += 1
					root.update()

				play_stream.stop_stream()
				play_stream.close()
	
				p_aud.terminate()
	
	# Live Audio
	#def live_audio(self, input_device)
	#	p_live = pyaudio.PyAudio()
	#	live_stream = p_live.open(
	#	format = pyaudio.paInt16,
	#	channels = 1, # mono
	#	rate = 44100, # sample rate of 44100 Hz
	#	input = True, # input
	#	input_device_index = input_device, # probably 2 for guitar (probably feedback w/ mic)
	#	output = True, # output
	#	frames_per_buffer=1024)

		#print("* recording")
	#	num_samps = 1024

	#	while self.live_on is True: # Record
	#		live_samps = rec_stream.read(num_samps)
	#		self.live_data = rec_samps # pyaudio data
	#		self.live_data_np = np.fromstring(rec_samps, dtype=np.int16) # pyaudio data converted to numpy
	#		live_out = self.run_instruswitch
	#		live_stream.write(live_out, 1024)
	#		root.update()

		#print("* done")

	#	live_stream.stop_stream()
	#	live_stream.close()

	#	p_live.terminate()
	
	# Get File Path for WAV File
	def wav_file_path(self):
		self.wave_path = tkFileDialog.askopenfilename()
		self.wptext.delete('1.0', END)
		self.wptext.insert(INSERT,self.wave_path)
		self.play_button["state"] = NORMAL
		self.stop_audio_button["state"] = NORMAL
		
	# Run Aubio Demo
	def run_pitch_track(self):
		self.sr = self.sr_entry.get()
		self.sr = int(float(self.sr))
		os.system('python test_aubio.py %s %d' % (self.wave_path,self.sr))

	# Run InstruSwitch
#	def run_instruswitch(self):
		
	
	# Input Select		
	def rb_select(self):
		self.rb_sel =  self.rbvar.get()
		if self.rb_sel is 1: # File Upload Selected
			self.record_button["state"] = DISABLED
			self.sr_entry["state"] = NORMAL
			self.wpath["state"] = NORMAL
			self.input_mb["state"] = DISABLED
		if self.rb_sel is 2: # Record Selected
			self.record_button["state"] = NORMAL
			self.sr_entry["state"] = DISABLED
			self.wpath["state"] = DISABLED
			self.input_mb["state"] = NORMAL
		if self.rb_sel is 3: # Live Selected
			self.record_button["state"] = NORMAL
			self.sr_entry["state"] = DISABLED
			self.wpath["state"] = DISABLED
			self.input_mb["state"] = NORMAL
			
	# Record
	def record_start(self):
		if self.rb_sel is 2:
			self.mb_sel =  self.mbvar.get()
			if self.mb_sel == 1: # Mic as Input
				self.rec_on = True
				print "Recording..."
				self.record_audio(0)
			if self.mb_sel == 2: # External as Input
				self.rec_on = True
				print "Recording..."
				self.record_audio(2)
		#if self.rb_sel is 3:
		#	self.live_on = True
		#	print "Live..."
		#	self.live_audio(2)
		
	# Stop (Record)
	def stop_rec(self):
		if self.rec_on is True:
			self.rec_on = False
			print "Finished Recording"
			self.play_button["state"] = NORMAL
			self.stop_audio_button["state"] = NORMAL
			self.save_button["state"] = NORMAL

	# Stop (Play)		
	def stop_play(self):
		if self.play_on is True:
			self.play_on = False
				
	# Save Files
	def save_file(self):
		self.audio_sel =  self.playbvar.get()
		if self.audio_sel is 1: # Save Original
			if self.rb_sel is 2: # Save Recording
				self.save_path = self.save_entry.get()
				waveFile = wave.open(self.save_path, 'wb')
				waveFile.setnchannels(1)
				waveFile.setsampwidth(self.audio_rec.get_sample_size(pyaudio.paInt16))
				waveFile.setframerate(44100)
				waveFile.writeframes(b''.join(self.rec_data))
				waveFile.close()

	# Plot
	def plot_input(self):
		fig1 = Figure(figsize=(5,5), dpi=100)
		a1 = fig1.add_subplot(111)
		if self.rb_sel is 1:
			1
		if self.rb_sel is 2:
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

	# Create Widgets
	def createWidgets(self): 
		# QUIT Button
		self.QUIT = Button(self)
		self.QUIT["text"] = "QUIT"
		self.QUIT["fg"]   = "red"
		self.QUIT["command"] =  self.quit
		self.QUIT.grid(row=0, column=0, sticky=NW)
	
	# Title
		self.title_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
		self.instruswitch_title = Label(self, text="InstruSwitch", font=self.title_font, bg="grey85")
		self.instruswitch_title.grid(row=0, columnspan=20, ipady=25)
	
	# Inputs
		self.input_font = tkFont.Font(family="Helvetica", size=24, weight="bold")
		self.input_label = Label(self, text="Select Inputs:                     ", bg= "cornflower blue", font=self.input_font)
		self.input_label.grid(row=1, columnspan=10, ipady=10, sticky=W, pady=5)
		
		# Upload, Record, Live
		self.rbvar = IntVar()
		self.file_rb = Radiobutton(self, text="File Upload", variable=self.rbvar, value=1, command=self.rb_select, bg="grey85")
		self.file_rb.grid(row=2, column=0, sticky=W, ipady=5)
		self.record_rb = Radiobutton(self, text="Record", variable=self.rbvar, value=2, command=self.rb_select, bg="grey85")
		self.record_rb.grid(row=3, column=0, sticky=W, ipady=5)
		self.live_rb = Radiobutton(self, text="Live", variable=self.rbvar, value=3, state=DISABLED, bg="grey85")
		self.live_rb.grid(row=4, column=0, sticky=W, ipady=5)
		
		# WAV File Load Button
		self.wpath = Button(self, text="Load WAV File",command=self.wav_file_path)
		self.wpath.grid(row=2, column=1)
		self.wptext = Text(self, height=1, width=40)
		self.wptext.insert(INSERT, "WAV Path")
		self.wptext.grid(row=2, column=2, columnspan=5)
	
		# Sample Rate Entry
		self.sr_label = Label(self, text="Sample Rate (Hz)", bg="grey85")
		self.sr_label.grid(row=2, column=8, columnspan=5, ipadx=5)
		self.sr_entry = Entry(self)
		self.sr_entry.insert(0, 44100)
		self.sr_entry.grid(row=2, column=14, columnspan=5)
		
		# Mic, External, Etc.		
		self.mbvar = IntVar()
		self.input_mb = Menubutton(self, text="Select Input")
		self.input_mb.grid(row=3, column=1)
		self.input_mb.menu = Menu(self.input_mb, tearoff=0)
		self.input_mb["menu"]  =  self.input_mb.menu
		self.input_mb.menu.add_radiobutton(label="Mic", variable=self.mbvar, value=1)
		self.input_mb.menu.add_radiobutton(label="External Instrument", variable=self.mbvar, value=2)

		
		# Record Button
		self.record_button = Button(self)
		self.record_button["text"] = "Record",
		self.record_button["command"] = self.record_start
		self.record_button["activeforeground"] = "red"
		self.record_button.grid(row=3, column=2)
		
		# Stop Button (Record)
		self.stop_button = Button(self, text="Stop", command=self.stop_rec)
		self.stop_button.grid(row=3, column=3, sticky=W)
		
	# Select Instrument Configuration
		self.instr_font = tkFont.Font(family="Helvetica", size=24, weight="bold")
		self.instr_label = Label(self, text="Select Output Instrument:", bg= "cornflower blue", font=self.instr_font)
		self.instr_label.grid(row=5, columnspan=8, ipady=10, sticky=W, pady=5)
		
		# Instrument Menu
		self.ibvar = IntVar()
		self.input_inst = Menubutton(self, text="Select Instrument")
		self.input_inst.grid(row=6, column=0, sticky=W)
		self.input_inst.menu = Menu(self.input_inst, tearoff=0)
		self.input_inst["menu"]  =  self.input_inst.menu
		self.input_inst.menu.add_radiobutton(label="Piano", variable=self.ibvar, value=1)
		self.input_inst.menu.add_radiobutton(label="Violin", variable=self.ibvar, value=2)
		self.input_inst.menu.add_radiobutton(label="Trumpet", variable=self.ibvar, value=3)
		self.input_inst.menu.add_radiobutton(label="Bass", variable=self.ibvar, value=4)
		
		# Transpose
		trans_var = IntVar()
		self.trans_slider = Scale(self, from_=-48, to=48, orient=HORIZONTAL, label="Transpose", variable=trans_var, bg="grey85")
		self.trans_slider.grid(row=6, column=1, columnspan=2) 
		
	# Run, Play, & Save
		
		self.rps_font = tkFont.Font(family="Helvetica", size=24, weight="bold")
		self.rps_label = Label(self, text="Run, Play, & Save:", bg= "cornflower blue", font=self.rps_font, anchor=W)
		self.rps_label.grid(row=5, column=8, columnspan=18, ipady=10, sticky=W+E, pady=5)
		
		# Run Button
		self.run_button = Button(self, text="Run InstruSwitch", command=self.run_pitch_track)
		self.run_button.grid(row=6, column=8, columnspan=3, pady=5)
		
		# Play Button
		self.play_button = Button(self, text="Play", state=DISABLED, command=self.play_audio)
		self.play_button.grid(row=7, column=8, sticky=W, pady=5)
		
		# Stop Button (Audio)
		self.stop_audio_button = Button(self, text="Stop", state=DISABLED, command=self.stop_play)
		self.stop_audio_button.grid(row=7, column=9, sticky=W, pady=5)
		
		# Original or Output Select
		self.playbvar = IntVar()
		self.play_orig_rb = Radiobutton(self, text="Original", variable=self.playbvar, value=1, bg="grey85")
		self.play_orig_rb.grid(row=7, column=15, sticky=W, ipady=5)
		self.play_out_rb = Radiobutton(self, text="Output", variable=self.playbvar, value=2, bg="grey85")
		self.play_out_rb.grid(row=7, column=17, sticky=W, ipady=5)
		
		# Save Buttons
		self.save_button = Button(self, text="Save", state=DISABLED, command=self.save_file)
		self.save_button.grid(row=8, column=8, sticky=W, pady=5)
		
		#self.save_label = Label(self, text="Save Path")
		#self.save_label.grid(row=8, column=9, columnspan=3)
		self.save_entry = Entry(self, width=30)
		self.save_entry.insert(INSERT, "Save Path")
		self.save_entry.grid(row=8, column=10, columnspan=15, sticky=W, pady=5)
	
		
		
		# Save/Play Selection
		#self.play_var = IntVar()
		#self.play_orig = Radiobutton(self, text="Play Original", variable=self.play_var, value=1, command=self.play_select)
		#self.play_orig.pack(anchor = NW)
		#self.play_out = Radiobutton(self, text="Play Output", variable=self.play_var, value=2, command=self.play_select)
		#self.play_out.pack(anchor = NW)
		
	# Plots, etc.

	# Initialize
		self.file_rb.invoke()
		self.rec_on = False
		
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.pack()
		self.createWidgets()

		

root = Tk()
app = Application(master=root)
app.configure(bg="grey85")
app.mainloop()
root.destroy()