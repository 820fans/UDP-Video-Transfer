import socket
import sys
import time
from init import *


jpeg_quality = 80
server_address = get_address('server')
client_address = get_address('client')
buffersize = 65507


if __name__ == '__main__':

    running = True

    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # sk.bind(client_address)
    tot_frame = 0
    time_sta = time.time()
    id = 0
    while(running):
        time.sleep(0.001)
        buffer = id 
        id+=1 
        if buffer is None:
            continue
        # print(len(buffer))

        if buffer > 1e10:
            print("The message is too large to be sent within a single UDP datagram. We do not handle splitting the message in multiple datagrams")
            sk.sendto(b"FAIL",server_address)
            continue
            
        sk.sendto(str(id).encode(encoding='utf-8'), server_address)
        tot_frame +=1
        if tot_frame % 100 ==0 :
            print("{:.2f}fps".format(tot_frame/(time.time()-time_sta)))
        if tot_frame == 10000:
            break



    print("Quitting..")
    grabber1.stop()
    grabber1.join()
    sk.close()

