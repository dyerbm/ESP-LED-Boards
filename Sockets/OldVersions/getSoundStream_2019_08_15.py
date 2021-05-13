# Python 2.7 code to analyze sound volume and interface with Arduino

import pyaudio  # from http://people.csail.mit.edu/hubert/pyaudio/
# import serial  # from http://pyserial.sourceforge.net/
import audioop
import time
import sys
from PyQt5.QtCore import QTimer
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
from multiprocessing.connection import Client
import threading

def main():
    RATE = 44100
    BUFFERSIZE = 2**10
    secToRecord = .01
    kill_threads = False
    has_new_audio = False
    audio_device_index = 2

    current_bpm = 0
    prev_beat_time = time.perf_counter()
    bpm_history = []
    y_avg_history = []
    low_freq_avg_history = []
    low_avg_counter = 0

    callback_beat_detected = lambda: None
    callback_new_song = lambda: None
    callback_pause = lambda: None

    min_bpm = 60
    max_bpm = 180
    pause_count = 0
    low_avg_counter = 0

    beatCounter=0
    
    message = dict(beat=False) #dictionary to send to visualizer

    buffers_to_record = int(RATE * secToRecord / BUFFERSIZE)
    if buffers_to_record == 0:
        buffers_to_record = 1
    samples_to_record = int(BUFFERSIZE * buffers_to_record)
    chunks_to_record = int(samples_to_record / BUFFERSIZE)
    sec_per_point = 1. / RATE

    p = pyaudio.PyAudio()
    # make sure the default input device is broadcasting the speaker output
    # there are a few ways to do this
    # e.g., stereo mix, VB audio cable for windows, soundflower for mac
    print("Using default input device: {:s}".format(p.get_device_info_by_index(2)['name']))
    in_stream = p.open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=RATE,
                                    input=True,
                                    frames_per_buffer=BUFFERSIZE,
                                    input_device_index = audio_device_index)

    audio = np.empty((chunks_to_record * BUFFERSIZE), dtype=np.int16)  

    try:
        c = Client(('localhost', 5000))
    except:
        print("no connection")
             

    while True:
        audio_string = in_stream.read(BUFFERSIZE)

        for i in range(chunks_to_record):
            audio[i*BUFFERSIZE:(i+1)*BUFFERSIZE] = np.fromstring(audio_string, dtype=np.int16)
        has_new_audio = True

        current_time = time.perf_counter()

        xs,ys = fft(audio,BUFFERSIZE,RATE)

        #analyse audio
        # Calculate average for all frequency ranges
        y_avg = np.mean(ys)
        y_avg_history.append(y_avg)

        # Track intensity
        y_avg_mean = np.mean(y_avg_history)
        if y_avg < y_avg_mean / 100:
            low_avg_counter += 1
        else:
            low_avg_counter = 0

        # Reset tracking if intensity dropped significantly for multiple iterations
        if y_avg < 50 or low_avg_counter > 50:
            print("low avg -> new song")
            current_bpm = 0
            prev_beat_time = time.perf_counter()
            bpm_history = []
            y_avg_history = []
            low_freq_avg_history = []
            low_avg_counter = 0
            callback_new_song()

        # Otherwise do normal beat detection
        else:
            # Calculate low frequency average
            low_freq = [ys[i] for i in range(len(xs)) if xs[i] < 500]
            low_freq_avg = np.mean(low_freq)

            # Calculate recent low frequency average
            low_freq_avg_history.append(low_freq_avg)
            recent_low_freq_avg = np.mean(low_freq_avg_history)

            # Calculate bass frequency average
            bass = low_freq[:int(len(low_freq) / 2)]
            bass_avg = np.mean(bass)

            # Check if there is a beat
            time_since_last_beat = current_time - prev_beat_time
            if (y_avg > 1000# Minimum intensity
                    and (
                            bass_avg > recent_low_freq_avg * 1.5  # Significantly more bass than before
                            or (
                                    low_freq_avg < y_avg * 1.2  #
                                    and bass_avg > recent_low_freq_avg
                            )
                    )
            ):
                # print(self.curr_time - self.prev_beat)
                if time_since_last_beat > 60 / max_bpm:
                    beatCounter+=1
                    print('beat', beatCounter)
                    bpm_detected = 60 / time_since_last_beat
                    if len(bpm_history) < 8:
                        if bpm_detected > min_bpm:
                            bpm_history.append(bpm_detected)
                    else:
                        # bpm_avg = int(numpy.mean(self.bpm_history))
                        if (current_bpm == 0 or abs(current_bpm - bpm_detected) < 35):
                            bpm_history.append(bpm_detected)
                            # Recalculate with the new BPM value included
                            current_bpm = reject_outliers(bpm_history)[-1]

                    #callback_beat_detected(current_time, current_bpm)
                    prev_beat_time = current_time

        # Detect pause in song when missing out more than 4 expected beats
        if current_bpm > 0 and current_time - prev_beat_time > 60 / current_bpm * 4.5:
            callback_pause()

        if len(low_freq_avg_history) > 100:
            low_freq_avg_history = low_freq_avg_history[50:]

        # Shorten avg list
        if len(y_avg_history) > 48:
            y_avg_history = y_avg_history[48:]

        # Keep two 8-counts of BPMs so we can maybe catch tempo changes
        if len(bpm_history) > 48:
            bpm_history = bpm_history[16:]

        #send dict to visualizer script
        try:
            c.send(message)
        except:
            pass

        #reset message
        #message[""]

def fft(audio, BUFFERSIZE, RATE, data=None, trim_by=10, log_scale=False, div_by=100):
    if not data: 
        data = audio.flatten()
    left, right = np.split(np.abs(np.fft.fft(data)), 2)
    ys = np.add(left, right[::-1])
    if log_scale:
        ys = np.multiply(20, np.log10(ys))
    xs = np.arange(BUFFERSIZE/2, dtype=float)
    if trim_by:
        i = int((BUFFERSIZE/2) / trim_by)
        ys = ys[:i]
        xs = xs[:i] * RATE / BUFFERSIZE
    if div_by:
        ys = ys / float(div_by)
    return xs, ys

def reject_outliers(data,m=2.):
    data = np.array(data)
    return data[abs(data-np.mean(data))<m*np.std(data)]


main()