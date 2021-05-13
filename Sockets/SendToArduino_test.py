import socket
import ssl
import sys
import time
import colorsys
import select
from multiprocessing.connection import Listener


class ESP:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.color = '0,100,0'

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class ESPs:
    def __init__(self, ESParr):
        self.ESPs = ESParr
    
    

def send_data(espList):
    for i in espList:
        sent = i.sock.sendto(i.color.encode(), (i.host, i.port))


def create_ESP(address, port, numESP):
    ESPList = []

    for i in range(numESP):
        currentESP = ESP(address, port)
        currentESP.connect()
        ESPList.append(currentESP)

    return ESPList

def update_ESPs(ESPs, port, startRange, endRange):
    for i in range(startRange, endRange):
        address = "192.168.1."+str(i)
        print(address)
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sent = sock.sendto("a".encode(), (address, port))
        sock.settimeout(1)
        #ready = select.select([sock],[],[],0.01)
        #if ready[0]:
        try:
            data, server = sock.recvfrom(4096)
            if(data):
                print(data)
                data = data.decode()
                info = data.split(',')
                print(info)
                ESPs[int(info[1])].host = info[0]
        except:
            pass
        finally:
            sock.close()
    
    print(ESPs[0].host)
    return(ESPs)


def main(conn):
    print('hi')
    ESPs = create_ESP('192.168.1.55',42069,55)
    print('hello')
    ESPs = update_ESPs(ESPs,42069,2,255)
    print('holla')

    #start = time.time()
    temp_col=""
    while True:
        #start = time.time()
        '''msg = conn.recv()
        #print(len(msg), len(ESPs))
        for i in range(len(msg)):
            #print(len(msg[i]))
            #print(msg)
            ESPs[i].color = str(msg[i][0])+','+str(msg[i][1])+','+str(msg[i][2])
        
        send_data(ESPs)
            
        print('*' * int(msg[i][0]/10))'''
        #end = time.time()
        #print(end-start)

        #print(msg)

        for j in range(360):
            RGB = colorsys.hsv_to_rgb(j/360., 1,1)
            print(RGB)
            for i in range(3):
                temp_col = temp_col + str(int(RGB[i]*255)) + ","
            for i in range(50):
                ESPs[i].color=temp_col
            #print(temp_col)
            
            send_data(ESPs)
            time.sleep(0.02)
            #print(RGB)
            temp_col=""

    #end = time.time()
    #print(end-start)


def mother(address):
    serv = Listener(address)
    while True:
        client = serv.accept()
        main(client)

main('ok')
mother(('', 5001)) 

main('ok')
#main()
