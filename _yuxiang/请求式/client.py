import socket
import cv2
import sys
from threading import Thread, Lock
import sys
import time


jpeg_quality = 80
host = '192.168.1.3'
port = 12340
server_address = (host, port)
client_address = ('192.168.1.8', port)
buffersize = 65507


class VideoGrabber(Thread):
    """ A threaded video grabber

    Attributes:
        encode_params (): 
        cap (str): 
        attr2 (:obj:`int`, optional): Description of `attr2`.
        
    """
    def __init__(self, jpeg_quality):
        """Constructor.
        Args:
        jpeg_quality (:obj:`int`): Quality of JPEG encoding, in 0, 100.
        
        """
        Thread.__init__(self)
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.buffer = None
        self.lock = Lock()

    def stop(self):
        self.running = False 
    
    def get_buffer(self):
        """Method to access the encoded buffer.
        Returns:
        np.ndarray: the compressed image if one has been acquired. 
        None otherwise.
        """
        if self.buffer is not None:
            self.lock.acquire()
            cpy = self.buffer.copy()            
            self.lock.release()
            return cpy # ndarray
    
    def run(self):
        # 一直读取
        while self.running:
            success, img = self.cap.read()
            if not success:
                continue
            time.sleep(0.001)
            # jpeg compression
            # Protected by a lock
            # As the main thread may asks to access the buffer
            self.lock.acquire()
            result, self.buffer = cv2.imencode('.jpg', img, self.encode_param)
            # result表示是否成功
            #print(type(result), type(self.buffer))
            self.lock.release()


if __name__ == '__main__':
    grabber1 = VideoGrabber(jpeg_quality)
    grabber1.start()

    running = True

    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sk.bind(client_address)

    while(running):
        # address是服务器的地址
        # print("正在等待服务器申请中...")
        data, address = sk.recvfrom(4)
        if(data == b"get"):
            buffer = grabber1.get_buffer()
            if buffer is None:
                continue
            # print(len(buffer))
            if len(buffer) > 65507:
                print("The message is too large to be sent within a single UDP datagram. We do not handle splitting the message in multiple datagrams")
                sk.sendto(b"FAIL",address)
                continue
            # We sent the buffer to the server
            sk.sendto(buffer.tobytes(), address)
        elif(data == b"quit"):
            grabber1.stop()
            running = False #终止循环

    print("Quitting..")
    grabber1.join()
    sk.close()

