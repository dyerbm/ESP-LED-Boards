import socket
import sys

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('192.168.1.119', 4210)
message = '255,255,255'

try:

    # Send data
    print('sending', message)
    sent = sock.sendto(message.encode(), server_address)

    # Receive response
    '''print('waiting to receive')
    data, server = sock.recvfrom(4096)
    print('received ', data)'''

finally:
    print('closing socket')
    sock.close()