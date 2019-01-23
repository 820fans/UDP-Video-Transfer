import socket
import cv2 
import numpy as np 
import sys 
import time 

cv2.namedWindow("test")

sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = '192.168.43.43'
port = 12340
server_address = (host, port)
client_address = ('192.168.43.6', port)
buffersize = 65507


while(True):
    # 先向client发送请求
    sent =  sk.sendto(b"get", client_address)

    data, client = sk.recvfrom(buffersize)
    #print("Fragment size : {}".format(len(data)))

    try:
        array = np.frombuffer(data, dtype=np.uint8)
    except:
        if data == b"FAIL": 
            continue
    
    img = cv2.imdecode(array, 1) #解码
    cv2.imshow("test", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


sent =  sk.sendto(b"quit", client_address)
print("The server is quitting. ")

