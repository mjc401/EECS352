#! /usr/bin/env python

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

import array_2_midi as array_midi
import pitch_track_fn as pitch_track
import midi_test

	

class Application(Frame):
	
# AUDIO (RECORD, PLAY, LIVE)
	# Record Audio
	def record_audio(self, input_device):
	
		# Open input stream
		self.audio_rec = pyaudio.PyAudio()
		rec_stream = self.audio_rec.open(
		format = pyaudio.paFloat32,
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
			self.rec_data_np.append(np.fromstring(rec_samps, dtype=np.float32)) # pyaudio data converted to numpy
			root.update() # make sure GUI can still update & not get stuck in loop

		self.rec_data_np = np.hstack(self.rec_data_np) # output numpy data array
		librosa.output.write_wav("rec_data.wav", self.rec_data_np, 44100)

		
		#waveFile = wave.open("rec_data.wav", 'wb')
		#waveFile.setnchannels(1)
		#waveFile.setsampwidth(4)
		#waveFile.setframerate(44100)
		#waveFile.writeframes(b''.join(self.rec_data))
		#waveFile.close()

		# Close Stream
		rec_stream.stop_stream()
		rec_stream.close()
		self.audio_rec.terminate()
		
	# Play Audio
	def play_audio(self):
		self.audio_sel =  self.playbvar.get()
		self.play_img_g = PhotoImage(file="./GUI_images/play_green.gif")
		if self.audio_sel == 1: # Play Original
			if self.rb_sel == 1: # From File Upload
				wav_play = wave.open(self.wave_path, 'rb')

				self.play_button["image"] = self.play_img_g
				
				p_aud = pyaudio.PyAudio()

				play_stream = p_aud.open(format=p_aud.get_format_from_width(wav_play.getsampwidth()),
				channels=wav_play.getnchannels(),
				rate=wav_play.getframerate(),
				output=True)

				play_data = wav_play.readframes(1024)
				self.play_on = True

				while play_data != '' and self.play_on == True:
					play_stream.write(play_data)
					play_data = wav_play.readframes(1024)
					root.update()

				play_stream.stop_stream()
				play_stream.close()
	
				p_aud.terminate()
				
				self.play_button["image"] = self.play_img
				
			elif self.rb_sel == 2: # From Recording
				p_aud = pyaudio.PyAudio()
				
				self.play_button["image"] = self.play_img_g

				play_stream = p_aud.open(
				format=pyaudio.paFloat32,
				channels=1,
				rate=44100,
				output=True)
				
				self.play_on = True
				i = 1
				play_data = self.rec_data_np[0:1023].astype(np.float32).tostring()

				while play_data != '' and self.play_on == True:
					play_stream.write(play_data)
					start = i*1023
					end = start + 1023
					play_data = self.rec_data_np[start:end].astype(np.float32).tostring()
					i += 1
					root.update()

				play_stream.stop_stream()
				play_stream.close()
	
				p_aud.terminate()
				
				self.play_button["image"] = self.play_img
				
		elif self.audio_sel == 2:
			p_aud = pyaudio.PyAudio()
				
			self.play_button["image"] = self.play_img_g

			play_stream = p_aud.open(
			format=pyaudio.paFloat32,
			channels=1,
			rate=44100,
			output=True)
				
			self.play_on = True
			i = 1
			play_data = self.output[0:1023].astype(np.float32).tostring()

			while play_data != '' and self.play_on == True:
				play_stream.write(play_data)
				start = i*1023
				end = start + 1023
				play_data = self.output[start:end].astype(np.float32).tostring()
				i += 1
				root.update()

			play_stream.stop_stream()
			play_stream.close()
	
			p_aud.terminate()
				
			self.play_button["image"] = self.play_img
			
			
	
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
	#def run_pitch_track(self):
	#	self.wav_run = wave.open(self.wave_path, 'rb')
	#	self.sr = self.wav_run.getframerate()
	#	os.system('python test_aubio.py %s %d' % (self.wave_path,self.sr))

	# Run InstruSwitch
	def run_instruswitch(self):
		self.plot_sel = self.plot_var.get() # Plot checkbox
		self.transpose_note = self.trans_var.get()
		
		self.output = []
		num_instrument = self.ibvar.get()
		if num_instrument == 1:
			instrument = "Piano"
		if num_instrument == 2:
			instrument = "Violin"
		if num_instrument == 3:
			instrument = "ASax"
		if num_instrument == 4:
			instrument = "EBass"

		if self.rb_sel == 1: # File Upload
			self.instru_samples = self.wave_path
			self.wav_run = wave.open(self.wave_path, 'rb')
			self.sr = self.wav_run.getframerate()
		else: # Record
			self.instru_samples = "rec_data.wav"
			self.sr = 44100
	
		pitch_data, s_length = pitch_track.pitch_track(self.instru_samples,self.sr,Display=self.plot_sel)
		self.midi_file = array_midi.array_to_MIDI(pitch_data, s_length)
		print self.midi_file
		self.output = midi_test.make_output(instrument, self.midi_file, self.transpose_note)
		
		self.play_button["state"] = NORMAL
		self.stop_audio_button["state"] = NORMAL
		self.save_button["state"] = NORMAL
		self.save_midi_button["state"] = NORMAL
		
		
	
	# Input Select		
	def rb_select(self):
		self.rb_sel =  self.rbvar.get()
		if self.rb_sel == 1: # File Upload Selected
			self.record_button["state"] = DISABLED
			#self.sr_entry["state"] = NORMAL
			self.wpath["state"] = NORMAL
			self.input_mb["state"] = DISABLED
		if self.rb_sel == 2: # Record Selected
			self.record_button["state"] = NORMAL
			#self.sr_entry["state"] = DISABLED
			self.wpath["state"] = DISABLED
			self.input_mb["state"] = NORMAL
		if self.rb_sel == 3: # Live Selected
			self.record_button["state"] = NORMAL
			#self.sr_entry["state"] = DISABLED
			self.wpath["state"] = DISABLED
			self.input_mb["state"] = NORMAL
			
	# Record
	def record_start(self):
		if self.rb_sel == 2:
			self.mb_sel =  self.mbvar.get()
			if self.mb_sel == 1: # Mic as Input
				self.rec_on = True
				print "Recording..."
				self.rec_red = PhotoImage(file="./GUI_images/record_red.gif")
				self.record_button["image"] = self.rec_red
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
		if self.rec_on == True:
			self.rec_on = False
			print "Finished Recording"
			self.record_button["image"] = self.rec_black
			self.play_button["state"] = NORMAL
			self.stop_audio_button["state"] = NORMAL
			self.save_button["state"] = NORMAL

	# Stop (Play)		
	def stop_play(self):
		if self.play_on == True:
			self.play_button["image"] = self.play_img
			self.play_on = False
				
	# Save Files
	def save_file(self):
		self.audio_sel =  self.playbvar.get()
		if self.audio_sel == 1: # Save Original
			if self.rb_sel == 2: # Save Recording
				self.save_path = tkFileDialog.asksaveasfilename(defaultextension=".wav")
				#waveFile = wave.open(self.save_path, 'wb')
				#waveFile.setnchannels(1)
				#waveFile.setsampwidth(self.audio_rec.get_sample_size(pyaudio.paFloat32))
				#waveFile.setframerate(44100)
				#waveFile.writeframes(b''.join(self.rec_data))
				#waveFile.close()
				#os.remove(self.save_path)
				librosa.output.write_wav(self.save_path, self.rec_data_np, 44100)
				
		if self.audio_sel == 2: # Save Output
			self.save_path = tkFileDialog.asksaveasfilename(defaultextension=".wav")
			librosa.output.write_wav(self.save_path, self.output, 44100)
			
	# Instrument Menu Text		
	def ib_sel(self):
		self.instr_menu = self.ibvar.get()
		if self.instr_menu == 1:
			self.input_inst["text"] = "Piano"
		elif self.instr_menu == 2:
			self.input_inst["text"] = "Violin"
		elif self.instr_menu == 3:
			self.input_inst["text"] = "Saxophone"
		elif self.instr_menu == 4:
			self.input_inst["text"] = "Bass"
			
	# Input Menu Text
	def input_sel(self):
		self.in_men_txt = self.mbvar.get()
		if self.in_men_txt == 1:
			self.input_mb["text"] = "Mic"
		elif self.in_men_txt == 2:
			self.input_mb["text"] = "External Instrument"
			
	# Save MIDI
	def save_midi(self):
		self.save_midi_path = tkFileDialog.asksaveasfilename(defaultextension=".mid")
		self.midi_file.save(self.save_midi_path)
		

	# Create Widgets
	def createWidgets(self): 
		# QUIT Button
		self.QUIT = Button(self)
		self.QUIT["text"] = "QUIT"
		self.QUIT["fg"]   = "red"
		self.QUIT["command"] =  self.quit
		self.QUIT.grid(row=0, column=0, sticky=NW)
	
	# Title
		ti = PhotoImage(file="./GUI_images/instruswitch.gif")
		ti = ti.subsample(4,4)
		self.title_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
		self.instruswitch_title = Label(self, text="InstruSwitch", font=self.title_font, bg="grey85",image=ti)
		self.instruswitch_title.image = ti
		self.instruswitch_title.grid(row=0, columnspan=20, rowspan=2, sticky=N)
		ti_sw = PhotoImage(file="./GUI_images/instru_switch_switch.gif")
		ti_sw = ti_sw.subsample(8,8)
		self.instruswitch_title_sw = Label(self, bg="grey85",image=ti_sw)
		self.instruswitch_title_sw.image = ti_sw
		self.instruswitch_title_sw.grid(row=0, column=20, columnspan=4, rowspan=2, sticky=N)


	
	# Inputs
		self.input_font = tkFont.Font(family="Helvetica", size=24, weight="bold")
		self.input_label = Label(self, text="Select Inputs:                     ", bg= "cornflower blue", font=self.input_font)
		self.input_label.grid(row=2, columnspan=10, ipady=10, sticky=W, pady=5)
		
		# Upload, Record, Live
		self.rbvar = IntVar()
		self.file_rb = Radiobutton(self, text="File Upload", variable=self.rbvar, value=1, command=self.rb_select, bg="grey85")
		self.file_rb.grid(row=3, column=0, sticky=W, ipady=5)
		self.record_rb = Radiobutton(self, text="Record", variable=self.rbvar, value=2, command=self.rb_select, bg="grey85")
		self.record_rb.grid(row=4, column=0, sticky=W, ipady=5)
		self.live_rb = Radiobutton(self, text="Live", variable=self.rbvar, value=3, state=DISABLED, bg="grey85")
		self.live_rb.grid(row=5, column=0, sticky=W, ipady=5)
		
		# WAV File Load Button
		self.wpath = Button(self, text="Load WAV File",command=self.wav_file_path)
		self.wpath.grid(row=3, column=1)
		self.wptext = Text(self, height=1, width=40)
		self.wptext.insert(INSERT, "WAV Path")
		self.wptext.grid(row=3, column=2, columnspan=5)
		
		# Mic, External, Etc.		
		self.mbvar = IntVar()
		self.input_mb = Menubutton(self, text="Select Input",width=15)
		self.input_mb.grid(row=4, column=1)
		self.input_mb.menu = Menu(self.input_mb, tearoff=0)
		self.input_mb["menu"]  =  self.input_mb.menu
		self.input_mb.menu.add_radiobutton(label="Mic", variable=self.mbvar, value=1,command=self.input_sel)
		self.input_mb.menu.add_radiobutton(label="External Instrument", variable=self.mbvar, value=2,command=self.input_sel)

		
		# Record Button
		self.record_button = Button(self)
		self.rec_black = PhotoImage(file="./GUI_images/record_black.gif")
		#self.record_button["text"] = "Record"
		self.rec_black = self.rec_black.subsample(1,1)
		self.record_button["command"] = self.record_start
		self.record_button["activeforeground"] = "red"
		self.record_button["image"] = self.rec_black
		self.record_button.image = self.rec_black
		self.record_button.grid(row=4, column=2)
		
		# Stop Button (Record)
		self.stop_button = Button(self, command=self.stop_rec)
		self.stop_img = PhotoImage(file="./GUI_images/stop.gif")
		self.stop_button["image"] = self.stop_img
		self.stop_button.grid(row=4, column=3, sticky=W)
		
	# Select Instrument Configuration
		self.instr_font = tkFont.Font(family="Helvetica", size=24, weight="bold")
		self.instr_label = Label(self, text="Select Output Instrument:", bg= "cornflower blue", font=self.instr_font)
		self.instr_label.grid(row=6, columnspan=8, ipady=10, sticky=W, pady=5)
		
		# Instrument Menu
		self.ibvar = IntVar()
		self.input_inst = Menubutton(self, text="Select Instrument",width=15)
		self.input_inst.grid(row=7, column=0, sticky=W,ipadx=10)
		self.input_inst.menu = Menu(self.input_inst, tearoff=0)
		self.input_inst["menu"]  =  self.input_inst.menu
		self.input_inst.menu.add_radiobutton(label="Piano", variable=self.ibvar, value=1,command=self.ib_sel)
		self.input_inst.menu.add_radiobutton(label="Violin", variable=self.ibvar, value=2,command=self.ib_sel)
		self.input_inst.menu.add_radiobutton(label="Saxophone", variable=self.ibvar, value=3,command=self.ib_sel)
		self.input_inst.menu.add_radiobutton(label="Bass", variable=self.ibvar, value=4,command=self.ib_sel)
		
		# Transpose
		self.trans_var = IntVar()
		self.trans_slider = Scale(self, from_=-48, to=48, orient=HORIZONTAL, label="Transpose", variable=self.trans_var, bg="grey85",resolution=1,length=130)
		self.trans_slider.grid(row=7, column=1, columnspan=2) 
		self.tr_label = Label(self, text="Semitones", bg="grey85")
		self.tr_label.grid(row=8, column=1, columnspan=2)
		
	# Run, Play, & Save
		
		self.rps_font = tkFont.Font(family="Helvetica", size=24, weight="bold")
		self.rps_label = Label(self, text="Run, Play, & Save:", bg= "cornflower blue", font=self.rps_font, anchor=W)
		self.rps_label.grid(row=6, column=8, columnspan=18, ipady=10, sticky=W+E, pady=5)
		
		# Run Button
		self.run_button = Button(self, text="Run InstruSwitch", command=self.run_instruswitch)
		self.run_button.grid(row=7, column=8, columnspan=3, pady=5)
		
		# Play Button
		self.play_button = Button(self, state=DISABLED, command=self.play_audio)
		self.play_img = PhotoImage(file="./GUI_images/play_black.gif")
		self.play_button["image"] = self.play_img
		self.play_button.grid(row=8, column=8, sticky=W, pady=5)
		
		# Stop Button (Audio)
		self.stop_audio_button = Button(self, state=DISABLED, command=self.stop_play)
		self.stop_audio_button["image"] = self.stop_img
		self.stop_audio_button.grid(row=8, column=9, sticky=W, pady=5)
		
		# Original or Output Select
		self.playbvar = IntVar()
		self.play_orig_rb = Radiobutton(self, text="Original", variable=self.playbvar, value=1, bg="grey85")
		self.play_orig_rb.grid(row=8, column=15, sticky=W, ipady=5)
		self.play_out_rb = Radiobutton(self, text="Output", variable=self.playbvar, value=2, bg="grey85")
		self.play_out_rb.grid(row=8, column=17, sticky=W, ipady=5)
		
		# Save Buttons
		self.save_button = Button(self, text="Save", state=DISABLED, command=self.save_file)
		self.save_button.grid(row=9, column=8, sticky=W, pady=5)
		
		self.save_midi_button = Button(self, text="Save Midi File", state=DISABLED, command=self.save_midi)
		self.save_midi_button.grid(row=9,column=1)
	
		# Store Play
		'''self.store1_label = Label(self, text="Store 1", bg="grey85")
		self.store1_label.grid(row=10, column=8)	
		
		self.store2_label = Label(self, text="Store 2", bg="grey85")
		self.store2_label.grid(row=11, column=8)		
		
		self.store1_button = Button(self, text="Store", state=DISABLED, )#command=self.store1)
		self.store1_button.grid(row=10, column=9, sticky=W, pady=5)
		
		self.store2_button = Button(self, text="Store", state=DISABLED, )#command=self.store2)
		self.store2_button.grid(row=11, column=9, sticky=W, pady=5)
		
		self.play_store1_button = Button(self, state=DISABLED)
		self.play_store1_button["image"] = self.play_img
		self.play_store1_button.grid(row=10, column=11, pady=5)
		
		self.stop_store1_button = Button(self, state=DISABLED)
		self.stop_store1_button["image"] = self.stop_img
		self.stop_store1_button.grid(row=10, column=12, pady=5)
		
		self.play_store2_button = Button(self, state=DISABLED)
		self.play_store2_button["image"] = self.play_img
		self.play_store2_button.grid(row=11, column=11, pady=5)
		
		self.stop_store2_button = Button(self, state=DISABLED)
		self.stop_store2_button["image"] = self.stop_img
		self.stop_store2_button.grid(row=11, column=12, pady=5)'''
		
	# Plots, etc.
		self.plot_var = IntVar()
		self.plot = Checkbutton(self, text="Plot", variable=self.plot_var,bg="grey85")
		self.plot.grid(row=7,column=3,padx=5)

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
root.update_idletasks()
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
size = tuple(int(_) for _ in root.geometry().split('+')[0].split('x'))
x = w/2 - size[0]/2
y = h/2 - size[1]/2
root.geometry("%dx%d+%d+%d" % (size + (x, y)))
root.lift()
root.attributes("-topmost", True)
root.attributes("-topmost", False)
root.wm_title("InstruSwitch v1.0")
app.mainloop()
if app.rb_sel == 2:
	os.remove("rec_data.wav")
root.destroy()