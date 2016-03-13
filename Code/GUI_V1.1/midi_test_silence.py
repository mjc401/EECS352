import mido
import librosa
import numpy as np

def make_output(instrument, midi_file):
	# All Piano Notes
	midi_to_note = ["A0", "A#0", "B0", "C1", "C#1", "D1", "D#1", "E1", "F1", 
					"F#1", "G1", "G#1", "A1", "A#1", "B1", "C2", "C#2", "D2", 
					"D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2", 
					"C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", 
					"A3", "A#3", "B3", "C4", "C#4", "D4", "D#4", "E4", "F4",
					"F#4", "G4", "G#4", "A4", "A#4", "B4", "C5", "C#5", "D5",
					"D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5",
					"C6", "C#6", "D6", "D#6", "E6", "F6", "F#6", "G6", "G#6", 
					"A6", "A#6", "B6", "C7", "C#7", "D7", "D#7", "E7", "F7", 
					"F#7", "G7", "G#7", "A7", "A#7", "B7", "C8"]

	# Open file
	print "It's me bitches"
	mid = midi_file
	mid.save("midi_output.mid")
	signal = np.zeros(1)

	i = 0 # so we can grab the next message using i+1
	messages = list(mid.play()) # turn generator into a list so we can index
								# into it. This is the list of midi messages

	for message in messages:
		# Only deal with on messages, get off messages with indexing using i+1
		if message.type == "note_on":
			# if time > 0 on a note_on message, because the last note was a 
			# note_off, there is silence between the two
			if message.time > 0:
				# Calculate the number of silent frames and add it to the signal
				num_silence_frames = int(message.time * 44100)
				silence = np.zeros(num_silence_frames)
				signal = np.append(signal, silence)

			# Get duration of the note
			"""try:
				duration = messages[i+1].time + messages[i+2].time
			except IndexError:"""
			duration = messages[i+1].time

			# Create string with path to appropriate file, subtract 21 from midi 
			# note b/c they start at 21
			filename = "../../Samples/SoundBank/" + instrument + "/" + instrument + \
				midi_to_note[message.note-21] + ".wav"
			
			# load the file from the soundbank
			current_note, sr = librosa.load(filename, sr=44100)
			# calculate the number of frames needed of the note
			num_frames = int(duration * sr)
			length = len(current_note)

			# if the # of frames we need is less than the number of 
			# frames in the soundbank file, great. Cut it short
			if num_frames <= length:
				current_note = current_note[:num_frames]
			# if we need a file longer than the one in the soundbank,
			# keep appending the last frame of the note onto the note until
			# it's as long as we need it to be
			else:
				last_frame = current_note[length-1]
				while num_frames < length:
					current_note = np.append(current_note, last_frame)

			# finally, add our current note to the signal
			signal = np.append(signal, current_note)

		# for debugging/observation
		# print message



		i += 1
	return signal