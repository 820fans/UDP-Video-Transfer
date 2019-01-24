from threading import Thread
from queue import Queue
import socket
import time
import cv2
import numpy
from config import Config

class Packer:
    """
    专门用于数据打包
    """
    def __init__(self, queue_size=128):
		#压缩参数，后面cv2.imencode将会用到，对于jpeg来说，15代表图像质量，越高代表图像质量越好为 0-100，默认95
        self.encode_param=[int(cv2.IMWRITE_JPEG_QUALITY), 60]

        self.init_config()
        # 这里的队列，用于多线程压缩图片之后，放入队列
        # Python的队列是线程安全的
        self.Q = Queue(maxsize=queue_size)
    
    def init_config(self):
        config = Config()
        # 初始化相机信息
        w = int(config.get("camera", "w"))
        h = int(config.get("camera", "h"))
        d = int(config.get("camera", "d"))
        self.frame_pieces = frame_pieces = int(config.get("camera", "pieces"))
        self.frame_size = w*h
        self.piece_size = int(w*h*d/frame_pieces)
        self.idx_frame = int(h/self.frame_pieces) # 一块数据，在原始图像占多少行

        # 初始化打包头信息
        self.head_name = config.get("header", "name")
        self.head_data_len_len = int(config.get("header", "data"))
        self.head_index_len = int(config.get("header", "index"))
        self.head_time_len = int(config.get("header", "time"))

        # 当前的设计下，head_len=16
        self.head_len = len(self.head_name) + self.head_data_len_len + self.head_index_len + self.head_time_len
        self.pack_len = self.head_len + self.piece_size # 46096


    def slice_data(self, frame_string):
        pass

    def pack_data(self, data_len, index, create_time, data):
        """
        Pack data over udp
        """
        res = b''
        res += self.head_name.encode()
        res += data_len.to_bytes(self.head_data_len_len, byteorder="big")
        res += index.to_bytes(self.head_index_len, byteorder="big")
        res += create_time.to_bytes(self.head_time_len, byteorder="big")
        
        res += data
        
        # intialize compress thread
        # thread = Thread(target=self.compress, args=(index, frame_raw,))
        # thread.daemon = True

        return res

    def compress(self, idx, frame_raw):
        result, imgencode = cv2.imencode('.jpg', frame_raw[i*self.idx_frame:(i+1)*self.idx_frame], self.encode_param)
        # print(len(imgencode))
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

    def unpack_header(self, head_block):
        name = head_block[:4]
        data_len = int.from_bytes(head_block[4:8], byteorder='big')
        index = int.from_bytes(head_block[8:9], byteorder='big')
        create_time = int.from_bytes(head_block[9:self.head_len], byteorder='big')
        return name, data_len, index, create_time