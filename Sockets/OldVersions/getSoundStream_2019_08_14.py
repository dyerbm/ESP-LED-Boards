# Python 2.7 code to analyze sound volume and interface with Arduino

import pyaudio  # from http://people.csail.mit.edu/hubert/pyaudio/
# import serial  # from http://pyserial.sourceforge.net/
import audioop
import time
import sys
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
from multiprocessing.connection import Client


def list_devices():
    # List all audio input devices
    p = pyaudio.PyAudio()
    i = 0
    n = p.get_device_count()
    while i < n:
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print(str(i)+'. '+dev['name'])
        i += 1


def arduino_soundlight():
    chunk = 1024  # Change if too fast/slow, never less than 1024
    scale = 20   # Change if too dim/bright
    exponent = 4    # Change if too little/too much difference between loud and quiet sounds
    bitrate = 44100

    # CHANGE THIS TO CORRECT INPUT DEVICE
    # Enable stereo mixing in your sound card
    # to make you sound output an input
    # Use list_devices() to list all your input devices
    device = 2

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=bitrate,
                    input=True,
                    frames_per_buffer=chunk,
                    input_device_index=device)

    print("Starting, use Ctrl+C to stop")
    try:
        # frequency index = frequency/bitrate*chunk_size
        Lfq1 = int(10/bitrate*chunk)
        Hfq1 = int(300/bitrate*chunk)
        Lfq2 = int(300/bitrate*chunk+1)
        Hfq2 = int(600/bitrate*chunk)
        Lfq3 = int(600/bitrate*chunk+1)
        Hfq3 = int(1000/bitrate*chunk)
        Lfq4 = int(1000/bitrate*chunk+1)
        Hfq4 = int(2000/bitrate*chunk)
        Lfq5 = int(2000/bitrate*chunk+1)
        Hfq5 = int(4000/bitrate*chunk)
        Lfq6 = int(4000/bitrate*chunk+1)
        Hfq6 = int(16000/bitrate*chunk)

        fq_avg1, fq_avg2, fq_avg3, fq_avg4, fq_avg5, fq_avg6 = 0,0,0,0,0,0

        timer = [time.time()]*6
        lastBeat = [0]*6
        beatCounter=0

        c = Client(('localhost', 5000))
        while True:
            #start = time.time()
            data = np.fromstring(stream.read(chunk), dtype=np.int16)

            w = np.fft.fft(data) #get the fft
            
            
            #print(Lfq_avg, Hfq_avg)
            for i in range(6):
                lastBeat[i] = time.time()-timer[i]
            
            msg =[0,0,0,0,0,0] #message should be in format [0-200, 200-400,400-800,800-2000,2000-4000,4000-16000] with sum of frequency ranges


            if (lastBeat[0]>0.1 and fq_avg1*1.5 < sum(np.abs(w[Lfq1:Hfq1])) > 10000):
                print('low', beatCounter)
                beatCounter += 1
                msg[0]=sum(np.abs(w[Lfq1:Hfq1]))
                timer[0] = time.time()
            if(lastBeat[1]>0.1 and fq_avg2*1.5 < sum(np.abs(w[Lfq2:Hfq2])) > 10000):
                beatCounter+=1
                msg[1]=sum(np.abs(w[Lfq2:Hfq2]))
                timer[1]=time.time()
            if(lastBeat[2]>0.1 and fq_avg3*1.5 < sum(np.abs(w[Lfq3:Hfq3])) > 10000):
                beatCounter+=1
                msg[2]=sum(np.abs(w[Lfq3:Hfq3]))
                timer[2]=time.time()
            if(lastBeat[3]>0.1 and fq_avg4*1.5 < sum(np.abs(w[Lfq4:Hfq4])) > 10000):
                beatCounter+=1
                msg[3]=sum(np.abs(w[Lfq4:Hfq4]))
                timer[3]=time.time()
            if(lastBeat[4]>0.1 and fq_avg5*1.5 < sum(np.abs(w[Lfq5:Hfq5])) > 10000):
                beatCounter+=1
                msg[4]=sum(np.abs(w[Lfq5:Hfq5]))
                timer[4]=time.time()
            if(lastBeat[5]>0.1 and fq_avg6*1.5 < sum(np.abs(w[Lfq6:Hfq6])) > 10000):
                beatCounter+=1
                msg[5]=sum(np.abs(w[Lfq6:Hfq6]))
                timer[5]=time.time()
            #update averages
            
            c.send(msg)

            #recalculate averages
            fq_avg1 = (0.9-lastBeat[0])*fq_avg1+(0.1+lastBeat[0])*sum(np.abs(w[Lfq1:Hfq1]))
            fq_avg2 = (0.9-lastBeat[1])*fq_avg2+(0.1+lastBeat[1])*sum(np.abs(w[Lfq2:Hfq2]))
            fq_avg3 = (0.9-lastBeat[2])*fq_avg3+(0.1+lastBeat[2])*sum(np.abs(w[Lfq3:Hfq3]))
            fq_avg4 = (0.9-lastBeat[3])*fq_avg4+(0.1+lastBeat[3])*sum(np.abs(w[Lfq4:Hfq4]))
            fq_avg5 = (0.9-lastBeat[4])*fq_avg5+(0.1+lastBeat[4])*sum(np.abs(w[Lfq5:Hfq5]))
            fq_avg6 = (0.9-lastBeat[5])*fq_avg6+(0.1+lastBeat[5])*sum(np.abs(w[Lfq6:Hfq6]))

            #end = time.time()
            #print(end-start)

    except KeyboardInterrupt:
        pass
    finally:
        print("\nStopping")
        stream.close()
        p.terminate()
# ser.close()


if __name__ == '__main__':
    ## IMPORTANT you'll need to set this to the stereo mixing ##
    list_devices()
    arduino_soundlight()
