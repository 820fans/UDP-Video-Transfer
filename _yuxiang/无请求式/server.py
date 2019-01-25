import socket
import cv2 
import numpy as np 
import sys 
import time 
from init import *

sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = get_address('server')
client_address = get_address('client')
buffersize = 65507

sk.bind(server_address)

tot_frame = 0
time_sta = time.time()

while(True):
    data, client = sk.recvfrom(buffersize)
    # print("接受成功")
    if data == b"FAIL": 
        print("buffersize is too small or lose the packet")
        continue
    array = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(array, 1) #解码
    cv2.imshow("test", img)

    tot_frame +=1
    if tot_frame % 100 ==0 :
        print("{:.2f}fps".format(tot_frame/(time.time()-time_sta)))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print("The server is quitting. ")

