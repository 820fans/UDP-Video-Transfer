import socket
import cv2 
import numpy as np 
import sys 
import time 

cv2.namedWindow("test")

sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = '192.168.1.3'
port = 12340
server_address = (host, port)

client_address = ('192.168.1.8', port)
buffersize = 65507

time_start=time.time()
total_delaytime = 0
total_frame = 0

while(True):
    # 先向client发送请求
    print("发送get请求")
    time_1 = time.time()
    sent =  sk.sendto(b"get", client_address)
    # sent =  sk.sendto(b"get", client_address)
    print("waiting camera data...")
    data, client = sk.recvfrom(buffersize)
    time_2=time.time()
    total_delaytime += (time_2 - time_1)
    print("get camera data")

    # print("Fragment size : {}".format(len(data)))
    
    if data == b"FAIL": 
        print("buffersize is too small or lose the packet")
        continue
    array = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(array, 1) #解码
    #print(img.shape)
    cv2.imshow("test", img)
    total_frame += 1
    if total_frame % 100 ==0:
        print("average fps: {:.2f}".format(total_frame/(time.time()-time_start)))
        print("average delay(in net): {:.2f}".format(total_delaytime / total_frame))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # print("即将进入下次循环...")


sent =  sk.sendto(b"quit", client_address)
print("The server is quitting. ")

