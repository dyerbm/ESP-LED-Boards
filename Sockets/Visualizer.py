import numpy as np
import time
import colorsys
import random
from multiprocessing.connection import Listener
from multiprocessing.connection import Client

class Visualizer:
    def __init__(self, numESPs=50):
        self.numESPs = numESPs
        self.colors = [(0,0,0)]*self.numESPs
        self.timer = time.time()
        self.lastBeat = 2.0
        self.visuals = 1
        self.newVis = True
        self.beatCounter=0
        self.changeBeat = random.randint(15,30)

        #other
        self.rotateColors = ((128,0,128) , (255,0,0) , (255,69,0) , (0,191,255) , (64,224,208) , (0,255,0) , (255,20,147))
        self.outerTables = {0:(0,1,2) , 1:(24,25,26) , 2:(3,4,5) , 3:(30,31,32) , 4:(9,10,11) , 5:(33,34,35), 6:(45,46,47) , 7:(21,22,23) , 8:(42,43,44), 9:(15,16,17), 10:(36,37,38) , 11:(12,13,14)}
        self.innerTables = {0:(27,28,29),1:(6,7,8),2:(18,19,20),3:(39,40,41)}

    def do_it(self, beat):

        if beat==True:
            self.beatCounter += 1
            if self.beatCounter >= self.changeBeat: #change visualizer, reset beat counter, determine new beats for change
                self.newVis=True
                self.changeBeat = random.randint(15,30)
                self.beatCounter = 0
                tempvis=self.visuals
                self.visuals = random.randint(0,2)
                print(self.visuals)
                if tempvis==self.visuals:
                    self.newVis=False

        #self.visuals=2 #force the color

        if beat==False:
            self.lastBeat = time.time()-self.timer
        else:
            self.timer = time.time()
            self.lastBeat = 0



        if self.visuals == 0:
            self.pulse(self.rotateColors[(int((self.beatCounter/5))%len(self.rotateColors))]) #choose a color and use it

        if self.visuals == 1:
            self.rainbow_rotate()

        if self.visuals == 2:
            self.large_rainbow()

        if self.visuals == 3:
            pass

        self.newVis=False
        


    def pulse(self, color):
        if self.lastBeat>=0.5:
            self.colors = [(0,0,0)]*self.numESPs
        else:
            red = int(color[0]*(0.5-self.lastBeat))
            green = int(color[1]*(0.5-self.lastBeat))
            blue = int(color[2]*(0.5-self.lastBeat))
            for i in range(self.numESPs):
                self.colors[i]=(red, green, blue)

    def rainbow_rotate(self):
        if self.newVis==True: #set up lights on a new beat
            for i in range(len(self.colors)):
                if i%3==0:
                    temp = colorsys.hsv_to_rgb(0,1,1)
                    self.colors[i] = [int(x*255) for x in temp]
                if i%3-1==0:
                    temp = colorsys.hsv_to_rgb(0.33,1,1)
                    self.colors[i] = [int(x*255) for x in temp]
                if i%3-2==0:
                    temp = colorsys.hsv_to_rgb(0.66,1,1)
                    self.colors[i] = [int(x*255) for x in temp]

        if self.lastBeat<0.04: #determine variance
            variance = 0.04-self.lastBeat
        else:
            variance = 0

        for i in range(len(self.colors)): #set new colors based on variance
            hsv_new = colorsys.rgb_to_hsv(self.colors[i][0]/255,self.colors[i][1]/255,self.colors[i][2]/255)[0]+0.002+variance
            if hsv_new>1:
                hsv_new -= 1

            c_new=colorsys.hsv_to_rgb(hsv_new,1,1)
            self.colors[i]=[int(x*255) for x in c_new]
        #print(self.colors[48])

    def large_rainbow(self):
        if self.newVis==True: #set lights on a new beat
            outerVar = 1/len(self.outerTables)
            innerVar = 1/len(self.innerTables)

            for i in range(len(self.outerTables)):
                for j in self.outerTables[i]:
                    temp=colorsys.hsv_to_rgb(outerVar*i,1,1)
                    self.colors[j] = [int(x*255) for x in temp]

            for i in range(len(self.innerTables)):
                for j in self.innerTables[i]:
                    temp=colorsys.hsv_to_rgb(innerVar*i,1,1)
                    self.colors[j] = [int(x*255) for x in temp]

        else: 
            if self.lastBeat<0.03: #find variance
                variance = 0.03-self.lastBeat
            else:
                variance = 0

            for i in range(len(self.outerTables)): #set outer lights
                for j in self.outerTables[i]:
                    hsv_new = colorsys.rgb_to_hsv(self.colors[j][0]/255,self.colors[j][1]/255,self.colors[j][2]/255)[0]+0.001+variance
                    if hsv_new>1:
                        hsv_new -= 1
                    c_new=colorsys.hsv_to_rgb(hsv_new,1,1)
                    self.colors[j]=[int(x*255) for x in c_new]

            for i in range(len(self.innerTables)): #set inner lights
                for j in self.innerTables[i]:
                    hsv_new = colorsys.rgb_to_hsv(self.colors[j][0]/255,self.colors[j][1]/255,self.colors[j][2]/255)[0]-0.001-variance
                    if hsv_new<0:
                        hsv_new += 1
                    c_new=colorsys.hsv_to_rgb(hsv_new,1,1)
                    self.colors[j]=[int(x*255) for x in c_new]


def main(conn): 
    c = Client(('localhost', 5001))
    visual = Visualizer()
    start = time.time()

    while True:
        data = conn.recv()

        visual.do_it(data['beat'])
        try:
            c.send(visual.colors)
        except:
            print('did not send')

        '''data = conn.recv()
        print(data['beat'])
        if data['beat']==True:
            start = time.time()
        lastBeat = time.time()-start
    
        msg = pulse(50, lastBeat,(139,0,139))


        try:
            c.send(msg) #mesage should be an array of rgb values
        except:
            pass'''
        



def mother(address):
    serv = Listener(address)
    while True:
        client = serv.accept()
        main(client)


mother(('', 5000)) 
