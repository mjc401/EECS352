import numpy as np, scipy as sp, matplotlib.pyplot as plt, matplotlib, sklearn, pyaudio, librosa
import analyse

trumpet,_ = librosa.load("clarinet_test.wav",sr=44100)
S = librosa.feature.melspectrogram(y=trumpet, sr=44100)
rms =  librosa.feature.rmse(y=trumpet)
#onset_env = librosa.onset.onset_strength(y=trumpet, sr=44100,S=S)
#strength = librosa.onset.onset_strength_multi(y=trumpet, sr=44100, S=S,channels=[0, 32, 64, 96, 128])
#detect = librosa.onset.onset_detect(y=trumpet, sr=44100)

s = np.zeros(200)
j=0

rms2 = rms[0] ** 2
#print rms2[0:30]
rms2_diff = np.diff(rms2)
#print rms_diff[0:30]
#for i in xrange(0,rms.shape[1]-4):
#	if rms2[i+4] - rms2[i] >= 2.25 and np.all(rms2_diff[i:i+4]>0) and np.all(rms2_diff[i:i+3]>1.25):
#		s[j] = i
#		j += 1
rms_diff = np.diff(rms[0])		
for i in xrange(0,rms.shape[1]-4):
	if rms[0,i+4] - rms[0,i] >= .5 and np.all(rms_diff[i:i+4]>0) and np.all(rms_diff[i:i+3]>.25):
		s[j] = i
		j += 1		

print s

plt.figure()
plt.subplot(3, 1, 1)
plt.plot(trumpet)
plt.xlim([0,len(trumpet)])
plt.subplot(3, 1, 2)
plt.semilogy(rms.T, label='RMS Energy')
plt.xlim([0, rms.shape[-1]])
plt.legend(loc='best')
plt.subplot(3, 1, 3)
plt.semilogy(rms.T ** 2, label='RMS Energy')
plt.xlim([0, rms.shape[-1]])
plt.legend(loc='best')

plt.vlines(s,10 ** -4,10,color='r',linestyle='--')
plt.show()

