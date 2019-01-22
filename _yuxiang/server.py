import socket 
import cv2 
import numpy as np 
# import simplejson


def recv_one_frame(conn):
    k = conn.recv(buffersize)
    try:
        k = np.frombuffer(k, dtype=np.uint8).reshape(h, w, c)
        return k
    except:
        return False



if __name__ == '__main__':
    h = 480
    w = 640
    c = 3
    buffersize = 3*640*480
    sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # socket.socket([family[, type[, proto]]])
    # family: 套接字家族可以使AF_UNIX或者AF_INET
    # type: 套接字类型可以根据是面向连接的还是非连接分为SOCK_STREAM或SOCK_DGRAM
    # protocol: 一般不填默认为0.

    host = socket.gethostname() # 获取本地主机名
    port = 1230                # 设置端口

    sk.bind((host,port))
    sk.listen(2)
    # 开始TCP监听。backlog指定在拒绝连接之前，
    # 操作系统可以挂起的最大连接数量。该值至少为1，大部分应用程序设为5就可以了。

    print("waiting for the client...")
    conn, address = sk.accept()# 被动接受TCP客户端连接,(阻塞式)等待连接的到来

    while True:
        frame = recv_one_frame(conn)
        if frame is False :
            continue
            print("网络不稳定！")
        else :
            cv2.imshow('test', frame)
            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                break

    conn.close()
    sk.close()
    cv2.destroyAllWindows()
