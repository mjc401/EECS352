import numpy as np, scipy as sp, matplotlib.pyplot as plt, matplotlib, sklearn, pyaudio, librosa
import math
from mido import Message, MidiFile, MidiTrack

# MIDI velocity function
def midi_velocity(signal, reference):
	x_sum = 0
	x_ref_sum = 0
	for i in signal:
		x_sum += i ** 2
	x_rms = math.sqrt(x_sum / len(signal))
	x_rms_dB = 20 * math.log10(x_rms / reference)
	midi_vel = round(127 * (10 ** (x_rms_dB / 40.)))
	return int(midi_vel)

# rms amplitude function
def rms_db(signal):
	x_sum = 0
	x_ref_sum = 0
	for i in signal:
		x_sum += i ** 2
	x_rms = math.sqrt(x_sum / len(signal))
	return x_rms

# load file and rms
trumpet,_ = librosa.load("clarinet_test.wav",sr=44100)
rms =  librosa.feature.rmse(y=trumpet)


# Initialize
onsets = np.zeros(200)
onsets_pos = np.zeros(200)
j=0
k=0

# RMS test
## Two criterion: one stricter (greater possibility of onset) and one less (possibility but should be checked with pitch data)
rms_diff = np.diff(rms[0])		
for i in xrange(0,rms.shape[1]-4):
	if (rms[0,i+4] - rms[0,i] >= .5 and np.all(rms_diff[i:i+4]>0) and np.all(rms_diff[i:i+3]>.25)) or (rms[0,i+2] - rms[0,i] > .71 and rms_diff[i] > .25) or np.all(rms_diff[i:i+8] > 0):
		if (rms[0,i+4] - rms[0,i] >= .5 and np.all(rms_diff[i:i+4]>0) and np.all(rms_diff[i:i+3]>.25)) or (rms[0,i+2] - rms[0,i] > .71 and rms_diff[i] > .25): # meets stricter criterion so more likely onset
			onsets[j] = i
			j += 1		
		else: # meets some critera, possible onset (check with pitch); soft onset
			onsets_pos[k] = i
			k+= 1

# Clean onsets so no consecutive
onsets_clean = onsets.copy()

for ii in xrange(0,len(onsets)):
	for iii in xrange(ii+1, len(onsets)):
		if abs(onsets[iii] - onsets[ii]) <= 4 or (onsets[iii] == 0 and iii != 0):
			onsets_clean[iii] = 0.5
			
onsets_clean = onsets_clean[onsets_clean != 0.5]

# MIDI velocity

# Get peak rms value for file to set as reference for velocity = 100
midi_vel_ref = []
sig_len = int(len(trumpet)/1024.)
for si in xrange(0,sig_len - 1):
	start = si * 1024
	stop = start + 1024
	midi_vel_ref = np.append(midi_vel_ref,rms_db(trumpet[start:stop]))
	
midi_vel_ref = np.amax(midi_vel_ref)

print midi_vel_ref
print rms_db(trumpet[0:512*130])
print rms_db(trumpet[512*130:512*155])
print rms_db(trumpet[512*155:512*175])
print midi_velocity(trumpet[0:512*130],midi_vel_ref)
print midi_velocity(trumpet[512*130:512*155],midi_vel_ref)
print midi_velocity(trumpet[512*155:512*175],midi_vel_ref)

# Test Data
test_data1 = [60,0,130,midi_velocity(trumpet[0:512*130],midi_vel_ref)]
test_data2 = [69,130,155,midi_velocity(trumpet[512*130:512*155],midi_vel_ref)]
test_data3 = [60,155,175,midi_velocity(trumpet[512*155:512*175],midi_vel_ref)]

test_data = np.array([[60,0,130,midi_velocity(trumpet[0:512*130],midi_vel_ref)],[69,130,155,midi_velocity(trumpet[512*130:512*155],midi_vel_ref)],[60,155,175,midi_velocity(trumpet[512*155:512*175],midi_vel_ref)]])

# Mido time works as tick differences so get amount between each event (1000 ticks per bar at 120 bpm, 512 samps per frame, & sample rate of 44100 Hz)
test_duration = (np.diff(np.sort(np.concatenate((test_data[:,1],test_data[:,2])))) * 512./44100*1000).astype(int)
#print test_duration

# write MIDI file
with MidiFile() as outfile:
	# Initialize
	track = MidiTrack()
	outfile.tracks.append(track)

	# add MIDI events
	track.append(Message('program_change', program=12))
	track.append(Message('note_on', note=test_data1[0], velocity=test_data1[3], time=int(test_data1[1]*512./44100*1000)))
	track.append(Message('note_off', note=test_data1[0], velocity=test_data1[3], time=test_duration[0]))
	track.append(Message('note_on', note=test_data2[0], velocity=test_data2[3], time=test_duration[1]))
	track.append(Message('note_off', note=test_data2[0], velocity=test_data2[3], time=test_duration[2]))
	track.append(Message('note_on', note=test_data3[0], velocity=test_data3[3], time=test_duration[3]))
	track.append(Message('note_off', note=test_data3[0], velocity=test_data3[3], time=test_duration[4]))

	outfile.save('test.mid') # output MIDI file


# Plot
plt.figure()
plt.subplot(3, 1, 1)
plt.plot(trumpet)
plt.xlim([0,len(trumpet)])
plt.subplot(3, 1, 2)
plt.semilogy(rms.T, '+-',label='RMS Energy')
plt.xlim([0, rms.shape[-1]])
plt.legend(loc='best')
plt.subplot(3, 1, 3)
plt.semilogy(rms.T ** 2, '+-',label='RMS Energy')
plt.xlim([0, rms.shape[-1]])
plt.legend(loc='best')

plt.vlines(onsets_clean,10 ** -4,10,color='r',linestyle='--',linewidth=10) # Red = cleaned onsets
plt.vlines(onsets,10 ** -4,10,color='y',linestyle='--') # Yellow = All strict onsets
plt.vlines(onsets_pos,10 ** -4,10,color='g',linestyle='--') # Green = Possible onsets (need to be checked)
plt.show()

