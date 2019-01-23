from threading import Thread
from queue import Queue
import socket
import cv2
import numpy
import time
import sys
from fps import FPS
from config import Config
import logging

logging.basicConfig(level=logging.DEBUG, 
                    filename='output.log',
					format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WebVideoStream:
	
	def __init__(self, src=0):
		self.config =  Config()
		# initialize the file video stream along with the boolean
		# used to indicate if the thread should be stopped or not
		self.stream = cv2.VideoCapture(src)
		self.stream.set(cv2.CAP_PROP_MODE, cv2.CAP_MODE_YUYV)
		self.stopped = False

		self.address = None
		self.sock = None
		self.init_connection()

		self.frame = None
		self.frame_size = 0
		self.piece_size = 0
		self.frame_pieces = 0
		self.init_config()
		
		#压缩参数，后面cv2.imencode将会用到，对于jpeg来说，15代表图像质量，越高代表图像质量越好为 0-100，默认95
		encode_param=[int(cv2.IMWRITE_JPEG_QUALITY), 50]
		
		# intialize thread
		self.thread = Thread(target=self.update, args=())
		self.thread.daemon = True

	def init_config(self):
		# 初始化大小信息
		config = self.config
		
		w = int(config.get("camera", "w"))
		h = int(config.get("camera", "h"))
		d = int(config.get("camera", "d"))
		self.frame_pieces = frame_pieces = int(config.get("camera", "pieces"))
		self.frame_size = w*h
		self.piece_size = w*h*d/frame_pieces

		# 初始化连接信息
		host = config.get("server", "host")
		port = config.get("server", "port")
		self.address = (host, int(port))

		# 初始化delay信息
		self.frame_delay = float(config.get("delay", "frame"))
		self.piece_delay = float(config.get("delay", "piece"))

		# 初始化打包头信息
		self.head_name = config.get("header", "name")
		self.head_data_len_len = int(config.get("header", "data"))
		self.head_index_len = int(config.get("header", "index"))
		self.head_time_len = int(config.get("header", "time"))
		

	def init_connection(self):
		try:
			self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		except socket.error as msg:
			print(msg)
			sys.exit(1)
	
	def close_connection(self):
		self.sock.close()

	def start(self):
		# start a thread to read frames from the file video stream
		self.thread.start()
		return self

	def slice_data(self, index, frame):
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
		return res

	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return

			# otherwise, read the next frame from the stream
			(self.grabbed, self.frame_raw) = self.stream.read()
			
			frame_s = self.frame_raw.flatten().tostring()

			for i in range(self.frame_pieces):
				time.sleep(0.001)
				self.frame = frame_s[i*46080:(i+1)*46080]+i.to_bytes(1, byteorder='big')

	def read(self):
		# return the frame most recently read
		if not self.frame:
			time.sleep(0.1)
		return self.frame

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True

def SendVideo():
	wvs = WebVideoStream().start()
	# fps = FPS().start()
	sock = wvs.sock
	address = wvs.address

	while True:
		frame = wvs.read()
		if frame:
			sock.sendto(frame, wvs.address)

	while False:
		#停止0.1S 防止发送过快服务的处理不过来，如果服务端的处理很多，那么应该加大这个值
		time.sleep(0.01)
		ret, frame = capture.read()

		# result, imgencode = cv2.imencode('.jpg', frame, encode_param)
		s = frame.flatten().tostring()

		# cur_time = time.time()
		# print(int(cur_time*1000))
		# continue
		
		for i in range(20):
			time.sleep(0.001)
			# print(i.to_bytes(1, byteorder='big'))
			sock.sendto(s[i*46080:(i+1)*46080]+i.to_bytes(1, byteorder='big'), address)

		# result, imgencode = cv2.imencode('.jpg', frame, encode_param)
		# data = numpy.array(imgencode)
		# stringData = data.tostring()
		
		# save data
		# cv2.imwrite('read video data.jpg', frame, encode_param)
		# show locally
		# cv2.imshow('read video data.jpg', frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
		
		# 读取服务器返回值
		# receive = sock.recvfrom(1024)
		# if len(receive): print(str(receive,encoding='utf-8'))
		# if cv2.waitKey(10) == 27: break
			
	# capture.release()
	# cv2.destroyAllWindows()
	# sock.close()

	
if __name__ == '__main__':
	SendVideo()
