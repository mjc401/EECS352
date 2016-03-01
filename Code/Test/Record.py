import numpy as np
import pyaudio



def record_audio(input_device):
	# Open input stream
	audio_rec = pyaudio.PyAudio()
	rec_stream = audio_rec.open(
	format = pyaudio.paInt16,
	channels = 1, # mono
	rate = 44100, # sample rate of 44100 Hz
	input_device_index = input_device, # input device (mic, external, etc.)
	frames_per_buffer=2048,
	input = True) # Input
	
	num_samps = 2048
	rec_data = []
	while Rec_on is True:
		rec_samps = rec_stream.read(num_samps)
		rec_data.append(rec_samps)
		root.update() # make sure GUI can still update & not get stuck in loop
	
	rec_stream.stop_stream()
	rec_stream.close()
	audio_rec.terminate()
	
	waveFile = wave.open("test_rec.wav", 'wb')
	waveFile.setnchannels(1)
	waveFile.setsampwidth(audio_rec.get_sample_size(pyaudio.paInt16))
	waveFile.setframerate(44100)
	waveFile.writeframes(b''.join(rec_data))
	waveFile.close()
	audio_rec.terminate()