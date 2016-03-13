#! /usr/bin/env python

import sys
import pyaudio
import librosa
#from aubio import source, pitch, freqtomidi
import sys, os.path
import numpy as np
from math import floor, log10, sqrt
from numpy import array, ma
import matplotlib.pyplot as plt
from demo_waveform_plot import get_waveform_plot, set_xlabels_sample2time


def pitch_track(filename, samplerate, Display=False):
    Display_Plot = Display

    from aubio import source, pitch, freqtomidi

    #########VARY this Value
    tolerance = 0.80
    silence_threshold = 0.02
    #####################
    # if len(sys.argv) < 2:
    #     print "Usage: %s <filename> [samplerate]" % sys.argv[0]
    #     sys.exit(1)

    #filename = sys.argv[1]

    downsample = 1
    samplerate = 44100 / downsample
    if len( sys.argv ) > 2: samplerate = int(sys.argv[2])

    win_s = 4096 / downsample # fft size
    hop_s = 512  / downsample # hop size

    s = source(filename, samplerate, hop_s)
    samplerate = s.samplerate

    # may be able to use onset tracking for silence threshold information

    pitch_o = pitch("yinfft", win_s, hop_s, samplerate)
    pitch_o.set_unit("midi")
    pitch_o.set_tolerance(tolerance)

    pitches = []
    confidences = []

    #****************************************************
    # total number of frames read
    total_frames = 0
    while True:
        samples, read = s()
        pitch = pitch_o(samples)[0]
        #pitch = int(round(pitch))
        confidence = pitch_o.get_confidence()
        #if confidence < 0.8: pitch = 0.
        #print "%f %f %f" % (total_frames / float(samplerate), pitch, confidence)
        pitches += [pitch]
        confidences += [confidence]
        total_frames += read
        if read < hop_s: break

    if 0: sys.exit(0)

    ####use librosa to get samples###
    signal, sr  = librosa.load(filename, sr = 44100)

    signal2 = []
    start = 0
    for i in range(512, len(signal), hop_s):
        end = i
        signal2.append(np.average(np.square(signal[start:end])))
        start = i

    uplist = []
    dlist = []
    for i in range( len(signal2)-2):
        if signal2[i+2] - signal2[i] > 0.1*signal2[i]:
            uplist.append(i)
        dlist.append(signal2[i+2]-signal2[i])

    ##GET PITCHES CONFIDENCES AND TIMES##
    skip = 1
    pitches = array(pitches[skip:])
    confidences = array(confidences[skip:])
    times = [t * hop_s for t in range(len(pitches))]
    #**************************************


    ground_truth = os.path.splitext(filename)[0] + '.f0.Corrected'
    if os.path.isfile(ground_truth):
        ground_truth = array_from_text_file(ground_truth)
        true_freqs = ground_truth[:,2]
        true_freqs = ma.masked_where(true_freqs < 2, true_freqs)
        true_times = float(samplerate) * ground_truth[:,0]
        ax2.plot(true_times, true_freqs, 'r')
        ax2.axis( ymin = 0.9 * true_freqs.min(), ymax = 1.1 * true_freqs.max() )

    cleaned_pitches = pitches
    cleaned_pitches = ma.masked_where(confidences < tolerance, cleaned_pitches)

    octave_cleaned = octave_error(cleaned_pitches)
    for i in range(1):
        octave_cleaned = octave_error3(octave_cleaned)
        octave_cleaned = silence_mask(octave_cleaned, signal2, silence_threshold)
        octave_cleaned = octave_error(octave_cleaned)
        

        
    #*****************************************************

    # load file and rms
    #trumpet,_ = librosa.load(filename,sr=44100)
    rms =  librosa.feature.rmse(y=signal)

    #create a velocity reference********************************************
    # Get peak rms value for file to set as reference for velocity = 100
    midi_vel_ref = []
    sig_len = int(len(signal)/1024.)
    for si in xrange(0,sig_len - 1):
        start = si * 1024
        stop = start + 1024
        midi_vel_ref = np.append(midi_vel_ref,rms_db(signal[start:stop]))
        
    midi_vel_ref = np.amax(midi_vel_ref)

    x_rms = rms_db(signal)                          #this is going to be the frames for the midi note
    #**********************************

    ###standalone onset detection
    #****************************************
    onsets_clean, onsets_pos = onset_detect(rms, Display = False)
    onsets_clean = np.array(onsets_clean, dtype = int)
    midi_out_new2, midi_out_new =midi_output(onsets_clean, octave_cleaned)

    print midi_out_new2, onsets_clean, midi_out_new

    for i in range(len(midi_out_new2)):
        start = midi_out_new2[i][1]
        stop = midi_out_new2[i][2]
        midi_vel = midi_velocity(signal[start*512:stop*512], midi_vel_ref)  #this is going to neeed the frames in signal
        midi_out_new2[i].append(midi_vel)
    #print results

    #*********************************************
	output = np.zeros((len(midi_out_new2), len(midi_out_new2[0])))
	
    for i in range(len(output)):
        for j in range(len(output[0])):
            output[i,j] = midi_out_new2[i][j]
    output = np.rint(output)
    output = np.array(output, dtype = int)

    if Display_Plot:
    ####PLOTTING######
    #****************************************************
        fig = plt.figure()
        ax1 = fig.add_subplot(311)
        ax1 = get_waveform_plot(filename, samplerate = samplerate, block_size = hop_s, ax = ax1)
        plt.setp(ax1.get_xticklabels(), visible = False)
        ax1.set_xlabel('')

        #plot cleaned pitches
        ax2 = fig.add_subplot(312, sharex = ax1)
        ax2.plot(times, pitches, '.g')
        ax2.plot(times, cleaned_pitches, '.-')
        ax2.plot(times, octave_cleaned, '.r' )
        plt.setp(ax2.get_xticklabels(), visible = False)
        ax2.set_ylabel('f0 (midi)')
        ax2.vlines(onsets_clean * 512,0,120,color='k',linestyle='--',linewidth=1)

        ##### plot confidence
        ax3 = fig.add_subplot(313, sharex = ax1)
        ax3.plot(times, confidences)
        ax3.plot(times, [tolerance]*len(confidences)) # draw a line at tolerance
        ax3.axis( xmin = times[0], xmax = times[-1])
        ax3.set_ylabel('condidence')
        set_xlabels_sample2time(ax3, times[-1], samplerate)

	plt.show(block=False)
    return output, len(signal)
    #**********************************************

def rms_db(signal):
    x_sum = 0
    x_ref_sum = 0
    for i in signal:
        x_sum += i ** 2
    x_rms = sqrt(x_sum / len(signal))
    return x_rms

def midi_velocity(signal, reference):
    x_sum = 0
    x_ref_sum = 0
    for i in signal:
        x_sum += i ** 2
    x_rms = sqrt(x_sum / len(signal))
    x_rms_dB = 20 * log10(x_rms / reference)
    midi_vel = round(127 * (10 ** (x_rms_dB / 40.)))
    return int(midi_vel)




def octave_error(in_array):
    winlen = 5             #window length = 2*n+1 must be odd number
    n = int(floor(winlen/2))
    out_array = in_array*1

    for i in range(n, int(len(in_array)-n)):
        win = in_array[i-n: i + n + 1]

        #look for octave error within 0.5 MIDI
        if 11.5 <= abs(in_array[i] - in_array[i+1])<= 12.5:  
            out_array[i-n: i + n + 1] = np.median(win) # this syntax works

    #repeat the above for the first n points
    for i in range(n):
        if 11.5 <= abs(in_array[i] - in_array[i+1])<= 12.5:  
            out_array[i] = np.median(out_array[0:int(n)]) 

    #repeat algorithm for last n points
    for i in range(len(in_array),int(len(in_array)-n)):
        if 11.5 <= abs(in_array[i] - in_array[i+1])<= 12.5:  
            out_array[i] = np.median(out_array[len(in_array):int(len(in_array)-n)]) 

    return out_array

def octave_error2(in_array):
    out_array = in_array*1
    idx_start = 0
    for i in range(len(in_array)-1):
        if (11.5> abs(in_array[i] - in_array[i+1])) or  (abs(in_array[i] - in_array[i+1])>12.5):
            idx_end = i
            out_array[idx_start:idx_end] = np.median(in_array[idx_start:idx_end])
            idx_start = i
        else:
            #print idx_start
            pass
    return out_array

def octave_error3(in_array):
    out_array = in_array*1
    idx_start = 0
    for i in range(len(in_array)-1):
        if round(abs(in_array[i] - in_array[i+1]))%12 ==  0:
            pass
        else:
            idx_end = i+1
            out_array[idx_start:idx_end] = np.median(in_array[idx_start:idx_end])
            idx_start = i
            #print idx_start
    return out_array


def octave_error4(in_array):
    out_array = in_array*1
    idx_start = 0
    for i in range(1,len(in_array)-1):
        if round(abs(in_array[i] - in_array[i+1]))%12 ==  0:
            pass
        else:
            idx_end = i+1
            out_array[idx_start:idx_end] = in_array[idx_start+ np.argmax(confidences[idx_start:idx_end])]
            idx_start = i
            #print idx_start
    return out_array


def mask_clean(in_array, mask_data):
    out_array = mask_data*1
    idx_start = 0
    for i in range(len(in_array)-1):
        if round(abs(in_array[i] - in_array[i+1]))%12 ==  0:
            pass
        else:
            idx_end = i
            out_array[idx_start:idx_end] = np.median(in_array[idx_start:idx_end])
            idx_start = i
            #print idx_start
    for i in range(len(out_array)-2,0,-1):
        #print i
        if out_array[i] == 0:
            out_array[i] = out_array[i+1]

    return out_array

def silence_mask(in_array, signal2, silence_threshold):
    out_array = in_array*1
    #print "len of raw signal is:", len(signal2)
    #print "len of 512 array is :", len(out_array)

    if len(out_array)>len(signal2):
       signal2 = np.hstack((signal2, 0))
    for i in range(len(in_array)):
        if signal2[i]<silence_threshold*np.max(signal2):
            out_array[i] = 0


    return out_array


def onset_detect(rms, Display = True):
    # Initialize
    onsets = np.zeros(200)
    onsets_pos = np.zeros(200)
    j=0
    k=0

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


    if Display:
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
        


    return onsets_clean, onsets_pos
            



def midi_output(onsets_clean, octave_cleaned):
    midi_out= []
    midi_out_new = []
    midi_out_new2 = []
    pitch_shift= []
    trans_list = []
    midi_start = 0
    midi_stop = 0
    midi_note = 0

    for i in range(len(octave_cleaned)-2): 
        if round(abs(octave_cleaned[i+1] - octave_cleaned[i+2]))%12 !=  0  or (octave_cleaned[i]==0  and octave_cleaned[i+1]>0) or (octave_cleaned[i]>0  and octave_cleaned[i+1]==0) or (i in onsets_clean):
            trans_list.append(i)
				
    trans_list.append(len(octave_cleaned))
	
    midi_start = trans_list[0]
    real_note = False
    for i in range(0,len(trans_list)-1):
        real_note = False
        if octave_cleaned[trans_list[i]+2] > 0:
            real_note = True
        if real_note:
            midi_start= trans_list[i]
            midi_stop = trans_list[i+1]
            midi_out.append([octave_cleaned[trans_list[i]+2],midi_start, midi_stop] )
	
    for i in range(len(midi_out)):
        if abs(midi_out[i][1] - midi_out[i][2]) >=6:
            midi_out_new.append(midi_out[i])

    i = 0
    #for i in range(len(midi_out_new)-1):
    while i < len(midi_out_new)-1:
        repeat = False
        j = i #when repeat is false
        while (midi_out_new[i][2] == midi_out_new[i+1][1]) and (midi_out_new[i][0] == midi_out_new[i+1][0]):
            midi_note = midi_out_new[j][0]
            midi_start = midi_out_new[j][1]
            midi_stop = midi_out_new[i+1][2]
            repeat = True
            #print "reating i", i, midi_stop
            i+=1
        if repeat:
            #print "repeat iteration:", i, [midi_note,midi_start,midi_stop]
            midi_out_new2.append([midi_note,midi_start,midi_stop])
            i +=1
        else:
            midi_out_new2.append(midi_out_new[j])
            #print "non repeat iteration:", i, midi_out_new[j]
            i +=1
        if i == len(midi_out_new)-1 and repeat == False:
             midi_out_new2.append(midi_out_new[i])

    return midi_out_new2, midi_out_new