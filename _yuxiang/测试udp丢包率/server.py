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
ans =[]

while(True):
    data, client = sk.recvfrom(buffersize)

    if data == b"FAIL": 
        print("buffersize is too small or lose the packet")
        continue
        
    data = data.decode(encoding='utf-8')
    ans.append(data)
    # tot_frame +=1
    # if tot_frame % 100 ==0 :
    #     print("{:.2f}fps".format(tot_frame/(time.time()-time_sta)))
    if data =='10000':
        break

f=open("ans.txt","w")
for line in ans:
    f.write(line+'\n')
f.close()

print("The server is quitting. ")

