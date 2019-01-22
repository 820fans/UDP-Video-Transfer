import socket 
import cv2 
import numpy as np

h = 48*4
w = 64*4
c = 3

def send_one_frame(sk):
    ret, frame = cap.read()
    sk.send(frame.tobytes())


if __name__ == '__main__':
    sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    host = '192.168.137.140' # 获取本地主机名
    port = 12340               # 设置端口号

    # 主动初始化TCP服务器连接，。一般ad dress的格式为元组（hostname,port），
    # 如果连接出错，返回socket.error错误。
    sk.connect((host, port))
    
    cap = cv2.VideoCapture(0)

    count = 10000

    while count:
        send_one_frame(sk)
        count = count - 1
        if count % 200 == 0 :
            print("{}帧".format(10000-count))

    sk.close()
    cap.release()
