import socket 
import cv2 

sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# socket.socket([family[, type[, proto]]])
# family: 套接字家族可以使AF_UNIX或者AF_INET
# type: 套接字类型可以根据是面向连接的还是非连接分为SOCK_STREAM或SOCK_DGRAM
# protocol: 一般不填默认为0.

host = socket.gethostname() # 获取本地主机名
port = 12345                # 设置端口

sk.bind((host,port))
sk.listen(5)
# 开始TCP监听。backlog指定在拒绝连接之前，
# 操作系统可以挂起的最大连接数量。该值至少为1，大部分应用程序设为5就可以了。

buffersize = 1024
print("waiting for the client...")

while True:
    conn, address = sk.accept()# 被动接受TCP客户端连接,(阻塞式)等待连接的到来
    # address是地址
    frame = conn.recv(buffersize)
    print(frame)
    conn.close()

sk.close()