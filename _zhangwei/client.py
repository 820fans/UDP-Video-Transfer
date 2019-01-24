from threading import Thread
from queue import Queue
import socket
import cv2
import numpy
import time
import sys
from fps import FPS
from config import Config
from packer import Packer
import logging

logging.basicConfig(level=logging.DEBUG, 
                    filename='output.log',
					format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WebVideoStream:
	
	def __init__(self, src=0):
		self.config = Config()
		self.packer = Packer()
		# initialize the file video stream along with the boolean
		# used to indicate if the thread should be stopped or not
		self.stream = cv2.VideoCapture(src)
		self.stream.set(cv2.CAP_PROP_MODE, cv2.CAP_MODE_YUYV)
		# print(self.stream.get(cv2.CAP_PROP_FPS)) # 默认帧率30
		self.stream.set(cv2.CAP_PROP_FPS, 20)   # cv version is 3.4.2
		self.stopped = False

		self.address = None
		self.sock = None
		self.init_connection()

		self.frame = None
		self.frame_size = 0
		self.piece_size = 0
		self.frame_pieces = 0
		self.init_config()
		
		# intialize thread
		self.thread = Thread(target=self.update, args=())
		self.thread.daemon = True

	def init_config(self):
		config = self.config
		# 初始化连接信息
		host = config.get("client", "host")
		port = config.get("client", "port")
		self.address = (host, int(port))

		# 初始化delay信息
		self.frame_delay = float(config.get("delay", "frame"))
		self.piece_delay = float(config.get("delay", "piece"))
		
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

	def update(self):
		piece_size = self.packer.piece_size
		# keep looping infinitely until the thread is stopped
		while True:
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return

			# otherwise, read the next frame from the stream
			(grabbed, frame_raw) = self.stream.read()
			
			frame_s = frame_raw.flatten().tostring()
			
			s = 0
			for i in range(self.packer.frame_pieces):
				time.sleep(0.005)
				now = int(time.time()*1000)
				data = frame_s[i*piece_size:(i+1)*piece_size]
				data_len = len(data)
				# t1 = time.time()
				# result, imgencode = cv2.imencode('.jpg', frame_raw[i*self.packer.idx_frame:(i+1)*self.packer.idx_frame], self.packer.encode_param)
				# t2 = time.time()
				# s += (t2-t1)
				# print(len(frame_raw[i*self.packer.idx_frame:(i+1)*self.packer.idx_frame].flatten().tostring()))
				# print(len(imgencode))
				res = self.packer.pack_data(data_len, i, now, data)
				self.frame = res
			# print("compress time for one image:",s)

	def read(self):
		# return the frame most recently read
		if not self.frame:
			time.sleep(0.1)
		return self.frame

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True

def SendVideo():
	
	t = 0
	if t == 0:
		wvs = WebVideoStream().start()
		# fps = FPS().start()
		sock = wvs.sock
		address = wvs.address

		while True:
			# t1 = time.time()
			frame = wvs.read()
			# t2 = time.time()
			# print(t2-t1)
			if frame:
				pass
				sock.sendto(frame, wvs.address)
	else:
		con = Config()
		host = con.get("server", "host")
		port = con.get("server", "port")
		address = (host, int(port))
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		capture = cv2.VideoCapture(0)
		capture.set(cv2.CAP_PROP_MODE, cv2.CAP_MODE_YUYV)
		#读取一帧图像，读取成功:ret=1 frame=读取到的一帧图像；读取失败:ret=0
		ret, frame = capture.read()
		encode_param=[int(cv2.IMWRITE_JPEG_QUALITY), 60]

		while True:
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
			#停止0.1S 防止发送过快服务的处理不过来，如果服务端的处理很多，那么应该加大这个值
			time.sleep(0.01)
			ret, frame = capture.read()
			frame = cv2.flip(frame, 1) # 水平翻转
			result, imgencode = cv2.imencode('.jpg', frame, encode_param)
			print(len(imgencode))
			s = frame.flatten().tostring()
		
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
		
		# 读取服务器返回值
		# receive = sock.recvfrom(1024)
		# if len(receive): print(str(receive,encoding='utf-8'))
		# if cv2.waitKey(10) == 27: break
			
	# capture.release()
	# cv2.destroyAllWindows()
	# sock.close()

	
if __name__ == '__main__':
	SendVideo()
