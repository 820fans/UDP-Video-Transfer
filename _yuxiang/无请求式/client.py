import socket
import sys
import time
from init import *
from camera import *


jpeg_quality = 80
server_address = get_address('server')
client_address = get_address('client')
buffersize = 65507


if __name__ == '__main__':
    grabber1 = VideoGrabber(jpeg_quality)
    grabber1.setDaemon(True)
    grabber1.start()

    running = True

    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # sk.bind(client_address)
    tot_frame = 0
    time_sta = time.time()
    while(running):
        time.sleep(0.001)
        buffer = grabber1.get_buffer()
        if buffer is None:
            continue
        # print(len(buffer))

        if len(buffer) > 65507:
            print("The message is too large to be sent within a single UDP datagram. We do not handle splitting the message in multiple datagrams")
            sk.sendto(b"FAIL",server_address)
            continue

        sk.sendto(buffer.tobytes(), server_address)
        tot_frame +=1
        if tot_frame % 100 ==0 :
            print("{:.2f}fps".format(tot_frame/(time.time()-time_sta)))

    print("Quitting..")
    grabber1.stop()
    grabber1.join()
    sk.close()

