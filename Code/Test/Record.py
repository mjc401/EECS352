import numpy as np
import pyaudio



def record_audio( input_device ):
	# Open input stream
	audio_rec = pyaudio.PyAudio()
	rec_stream = audio_rec.open(
	format = pyaudio.paInt16,
	channels = 1, # mono
	rate = 44100, # 44100 Hz sample rate
	input_device_index = input_device, # input device (mic, external, etc.)
	input = True) # Input
	
	num_samps = 1024
	rec_on = True
	rec_data = []
	print "1"
	while True:
		rec_samps = rec_stream.read( num_samps )
		rec_data.append(rec_samps)
		root.update()

		
def stop_record():
	rec_stream.stop_stream()
	rec_stream.close()
	audio_rec.terminate()