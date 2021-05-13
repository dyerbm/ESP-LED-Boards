import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 7777)
print('starting up on port', server_address)
sock.bind(server_address)

while True:
    print('\nwaiting to receive message')
    data, address = sock.recvfrom(4096)
    
    print('received' + str(len(data)) +'bytes from'+ str(address))
    print(data)
    
    if data:
        sent = sock.sendto(data, address)
        print('sent bytes back to', (sent, address))