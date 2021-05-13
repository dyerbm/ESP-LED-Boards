import socket
import ssl
import sys
import time
import colorsys


class ESP:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.color = '0,100,0'

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_data(espList):
    for i in espList:
        sent = i.sock.sendto(i.color.encode(), (i.host, i.port))


def create_ESP(startAddress, startPort, numESP):
    ESPList = []

    for i in range(numESP):
        addressEnd=str(int(startAddress[10:])+i)
        address=startAddress[0:10]+addressEnd
        port = startPort
        currentESP = ESP(address, port)
        currentESP.connect()
        ESPList.append(currentESP)

    return ESPList


def main():
    ESPs = create_ESP('192.168.1.55',42069,50)

    start = time.time()
    run=0
    temp_col=""
    while run==0:
        
        for j in range(360):
            RGB = colorsys.hsv_to_rgb(j/360., 1,1)
            for i in range(3):
                temp_col = temp_col + str(int(RGB[i]*255)) + ","
            for i in range(50):
                ESPs[i].color=temp_col
            print(temp_col)
            
            send_data(ESPs)
            time.sleep(0.02)
            print(RGB)
            temp_col=""

    end = time.time()
    print(end-start)


main()
