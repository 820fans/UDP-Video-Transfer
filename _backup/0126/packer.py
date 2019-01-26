from threading import Thread
# from queue import Queue
from collections import deque as Queue
import socket
import time
import cv2
import numpy
from config import Config
import logging

logging.basicConfig(level=logging.DEBUG, 
                    filename='output.log',
					format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Packer:
    """
    专门用于数据打包
    """
    def __init__(self):
		#压缩参数，后面cv2.imencode将会用到，对于jpeg来说，15代表图像质量，越高代表图像质量越好为 0-100，默认95
        self.encode_param=[int(cv2.IMWRITE_JPEG_QUALITY), 80]

        self.init_config()
        # 这里的队列，用于多线程压缩图片之后，放入队列
        # Python的队列是线程安全的
        self.Q = Queue()
    
    def init_config(self):
        config = Config()
        # 初始化相机信息
        self.w = w = int(config.get("camera", "w"))
        self.h = h = int(config.get("camera", "h"))
        self.d = d = int(config.get("camera", "d"))
        self.frame_pieces = frame_pieces = int(config.get("camera", "pieces"))
        self.frame_size = w*h
        self.frame_size_3d = w*h*d
        self.piece_size = int(w*h*d/frame_pieces)
        self.idx_frame = int(h/self.frame_pieces) # 一块数据，在原始图像占多少行

        # 初始化打包头信息
        self.head_name = config.get("header", "name")
        self.head_data_len_len = int(config.get("header", "data"))
        self.head_index_len = int(config.get("header", "index"))
        self.head_time_len = int(config.get("header", "time"))
        self.img_len = int(config.get("header", "data_size"))
        self.pack_len = int(config.get("header", "total_size"))
        # 当前的设计下，head_len=16
        self.head_len = len(self.head_name) + self.head_data_len_len + self.head_index_len + self.head_time_len
        # self.pack_len = self.head_len + self.piece_size # 46096

        # 初始化队列大小信息
        self.queue_size = int(config.get("receive", "queue_size"))
        self.frame_limit = int(config.get("receive", "frame_limit"))
        self.piece_limit = int(config.get("receive", "piece_limit"))

        self.queue_size = int(config.get("send", "queue_size"))
        self.send_piece_limit = int(config.get("send", "piece_limit"))
        self.send_piece_min = int(config.get("send", "piece_min"))

    def pack_data(self, index, create_time, data, Q):
        """
        Pack data over udp
        """
        if len(data) == 0:
            return None
        # intialize compress thread
        thread = Thread(target=self.compress, args=(index, create_time, data, Q))
        thread.daemon = True
        thread.start()

        # pack = None
        # while pack is None:
        #     pack = self.read_compress()

        # return pack

    def read_compress(self):
        # print(self.Q.qsize()) # 单机运行的时候，queue的长度持续增大
        # 拥塞控制(这里可以用个算法,时间限制就写简单点)
        frame = self.Q.get()
        # if self.Q.qsize() > self.queue_size*0.5: 
        #     self.Q = Queue()
        #     if self.Q.mutex:
        #         self.Q.queue.clear()
        return frame

    def compress(self, idx, create_time, frame_raw, Q):
        if len(frame_raw) == 0: return
        row_start = idx*self.idx_frame
        row_end = (idx+1)*self.idx_frame
        try:
            result, imgencode = cv2.imencode('.jpg', 
                frame_raw[row_start:row_end], self.encode_param)
        except:
            return
        if result:
            imgbytes = imgencode.tobytes()
            data_len = len(imgbytes)
            res = self.pack_header(data_len, idx, create_time)
            
            # 写入图像数据,需要padding
            # pad_bytes = b'\0' * (self.img_len - data_len)
            res += imgbytes
            # res += pad_bytes
            Q.append(res)
        return 1

    def unpack_data(self, res):
        data_len=0
        index=-1
        create_time=0
        data=b''
        if len(res) < self.head_len:
            return index, create_time, data
        head_block = res[:self.head_len]
        name, data_len, index, create_time = self.unpack_header(head_block)
        data_end = data_len + self.head_len
        body_block = res[self.head_len:data_end]
        
        return index, create_time, body_block

    def pack_header(self, data_len, index, create_time):
        res = b''
        res += self.head_name.encode()
        res += data_len.to_bytes(self.head_data_len_len, byteorder="big")
        res += index.to_bytes(self.head_index_len, byteorder="big")
        res += create_time.to_bytes(self.head_time_len, byteorder="big")
        return res

    def unpack_header(self, head_block):
        name = head_block[:4]
        data_len = int.from_bytes(head_block[4:8], byteorder='big')
        index = int.from_bytes(head_block[8:9], byteorder='big')
        create_time = int.from_bytes(head_block[9:self.head_len], byteorder='big')
        return name, data_len, index, create_time