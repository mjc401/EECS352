import numpy as np, scipy as sp, matplotlib.pyplot as plt, matplotlib, sklearn, pyaudio, librosa
import mido

# load file and rms
trumpet,_ = librosa.load("clarinet_test.wav",sr=44100)
rms =  librosa.feature.rmse(y=trumpet)


# Initialize
onsets = np.zeros(200)
onsets_pos = np.zeros(200)
j=0
k=0

# Squared rms (not used currently)
rms2 = rms[0] ** 2
rms2_diff = np.diff(rms2)
#print rms_diff[0:30]
#for i in xrange(0,rms.shape[1]-4):
#	if (rms2[i+3] - rms2[i] >= 1.25 and np.all(rms2_diff[i:i+3]>0) and np.all(rms2_diff[i:i+3]>1.25)) or rms2[i+1] - rms2[i] > .75:
#		s[j] = i
#		j += 1

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

#for i in xrange(0,rms.shape[1]-4):
#	if rms[0,i+4] - rms[0,i] >= .5 and np.all(rms_diff[i:i+4]>0) and np.all(rms_diff[i:i+3]>.25):
#		s[j] = i
#		j += 1


# Clean onsets so no consecutive
onsets_clean = onsets.copy()

for ii in xrange(0,len(onsets)):
	for iii in xrange(ii+1, len(onsets)):
		if abs(onsets[iii] - onsets[ii]) <= 4 or (onsets[iii] == 0 and iii != 0):
			onsets_clean[iii] = 0.5
			
onsets_clean = onsets_clean[onsets_clean != 0.5]



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

