import numpy as np, scipy as sp, matplotlib.pyplot as plt, matplotlib, sklearn, pyaudio, librosa

trumpet,_ = librosa.load("clarinet_test.wav",sr=44100)
rms =  librosa.feature.rmse(y=trumpet)
strength = librosa.onset.onset_strength_multi(y=trumpet, sr=44100)


plt.figure()
plt.subplot(2, 1, 1)
plt.semilogy(rms.T, label='RMS Energy')
plt.xlim([0, rms.shape[-1]])
plt.legend(loc='best')


plt.subplot(2, 1, 2)
librosa.display.specshow(strength, x_axis='time')
plt.title('Sub-band onset strength')
plt.show()