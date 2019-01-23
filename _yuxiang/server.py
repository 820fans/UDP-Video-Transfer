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

time_start=time.time()
total_delaytime = 0
total_frame = 0

while(True):
    # 先向client发送请求
    sent =  sk.sendto(b"get", client_address)

    data, client = sk.recvfrom(buffersize)
    time_end=time.time()
    #print("Fragment size : {}".format(len(data)))

    try:
        array = np.frombuffer(data, dtype=np.uint8)
    except:
        if data == b"FAIL": 
            continue
    
    img = cv2.imdecode(array, 1) #解码
    cv2.imshow("test", img)
    total_frame += 1
    total_delaytime += (time_end - time_start)
    if total_frame % 200 ==0:
        print("average fps: {:.2f}".format(total_frame/(time.time()-time_start)))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


sent =  sk.sendto(b"quit", client_address)
print("The server is quitting. ")

