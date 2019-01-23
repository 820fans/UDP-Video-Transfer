import socket 
import cv2 
import numpy as np 


def recv_one_frame(conn):
    frame = np.zeros((h, w, c), dtype=np.uint8)
    Id = 0
    blocksize = h // blocks 
    for i in range(blocks):
        k = conn.recv(buffersize)
        try:
            frame[Id:Id+blocksize] = np.frombuffer(k, dtype=np.uint8).reshape(blocksize, w, c)
        except:
            # frame[Id, Id+blocksize] = 0
            pass 
        Id += blocksize
    return frame


if __name__ == '__main__':
    h = 480
    w = 640
    c = 3
    blocks = 480
    assert h % blocks == 0
    buffersize = h * w * c // blocks
    sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # socket.socket([family[, type[, proto]]])
    # family: 套接字家族可以使AF_UNIX或者AF_INET
    # type: 套接字类型可以根据是面向连接的还是非连接分为SOCK_STREAM或SOCK_DGRAM
    # protocol: 一般不填默认为0.

    host = '192.168.43.43' # 获取本地主机名
    port = 12340                # 设置端口

    sk.bind((host,port))
    sk.listen(1)
    # 开始TCP监听。backlog指定在拒绝连接之前，
    # 操作系统可以挂起的最大连接数量。该值至少为1，大部分应用程序设为5就可以了。

    print("waiting for the client...")
    conn, address = sk.accept()# 被动接受TCP客户端连接,(阻塞式)等待连接的到来

    all_num = 0
    error_num = 0
    while True:
        all_num += 1
        frame = recv_one_frame(conn)
        if frame is False :
            print("网络不稳定！")
            error_num += 1 
            print ("掉包率{:.3f}%".format(error_num*100 / all_num))
            continue
        else :
            cv2.imshow('test', frame)
            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                break

    conn.close()
    sk.close()
    cv2.destroyAllWindows()
