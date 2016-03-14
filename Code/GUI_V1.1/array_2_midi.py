import numpy as np, scipy as sp, matplotlib.pyplot as plt, matplotlib, sklearn
from mido import Message, MidiFile, MidiTrack, MetaMessage


# Take pitch, frame, and velocity array and convert to midi data file
def array_to_MIDI(array,sig_length):

	# get relative times between events
	test_times = (np.diff(np.sort(np.concatenate((array[:,1],array[:,2])))* 512./44100)).astype(float)

	test_duration = (np.diff(np.sort(np.concatenate((array[:,1],array[:,2])))* 512./44100*960)).astype(int)
	#print array
	#print test_duration
	#print test_times
	#* 512./44100*960)
	# write MIDI file
	with MidiFile() as outfile:
		# Initialize
		track = MidiTrack()
		outfile.tracks.append(track)

		# add MIDI events
		track.append(Message('program_change', program=12))
		
		seg_skip_on = 1
		
		# take segments and make midi note events
		for segment in xrange(0,array.shape[0]):
			if segment == 0:
				track.append(Message('note_on', note=array[0,0], velocity=array[0,3], time=int(array[0,1]*512./44100*960)))
				track.append(Message('note_off', note=array[0,0], velocity=array[0,3], time=test_duration[0]))
			else:
				track.append(Message('note_on', note=array[segment,0], velocity=array[segment,3], time=test_duration[seg_skip_on]))
				seg_skip_off = seg_skip_on + 1
				track.append(Message('note_off', note=array[segment,0], velocity=array[segment,3], time=test_duration[seg_skip_off]))
				#print test_duration[seg_skip_off]
				seg_skip_on = seg_skip_off + 1
		track_end = int((sig_length/44100. - 512./44100 * array[-1,2])*960)
		track.append(Message('program_change', program=12, time=track_end))
		track.append(MetaMessage('end_of_track'))
				
		#outfile.save('output.mid') # output MIDI file
		
	return outfile