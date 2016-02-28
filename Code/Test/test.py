import pyaudio
import numpy as np
import analyse
import wave
import sys
import librosa

CHUNK = 1024

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

samps, sr = librosa.load(sys.argv[1], sr=44100)

#wf = wave.open(sys.argv[1], 'rb')

#p = pyaudio.PyAudio()

#stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
#                channels=wf.getnchannels(),
 #               rate=wf.getframerate(),
  #              output=True)

#samps = wf.readframes(CHUNK)

#samps = numpy.fromstring(wf, dtype=numpy.int16)
    # Show the volume and pitch
	
#print analyse.loudness(samps[:100]), analyse.musical_detect_pitch(samps[:100])

length = len(samps) / 1024
loudness = np.zeros(length)
pitch = np.zeros(length)

for i in xrange(0,length-1):
	loudness[i] = analyse.loudness(samps[i*CHUNK:(i+1)*CHUNK])
	pitch[i] = analyse.detect_pitch(samps[i*CHUNK:(i+1)*CHUNK], min_frequency=27.5, max_frequency=4000.0, samplerate=44100.0, sens=0.1, ratio=5.0)
	#if pitch[i]>0:
	#	pitch[i] = round(pitch[i])
	
	
np.savetxt("untitled.csv", pitch)
