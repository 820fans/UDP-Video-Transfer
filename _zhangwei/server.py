from threading import Thread
from queue import Queue, PriorityQueue
import socket
import time
import cv2
import numpy
import sys
from config import Config
from packer import Packer
import logging

logging.basicConfig(level=logging.DEBUG, 
                    filename='output.log',
					format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FramePack(object):
	def __init__(self, idx, ctime, frame):
		self.idx = idx
		self.ctime = ctime
		self.frame = frame
	
	def __cmp__(self, other):
		return cmp(other.ctime, self.ctime)

	def __lt__(self, other):
		return other.ctime < self.ctime

class NetVideoStream:
	def __init__(self, queue_size=128):
		self.stopped = False

		self.config = Config()
		self.packer = Packer()
		self.init_config()
		self.Q = PriorityQueue(maxsize=self.queue_size)
		self.Q = Queue(maxsize=self.queue_size)
		self.init_main_connection()

		# intialize thread
		self.thread = Thread(target=self.update, args=())
		self.thread.daemon = True

		# init timestamp
		self.last_frame = int(time.time()*1000)
		self.require = True

	def init_config(self):
		# 初始化大小信息
		config = self.config
		# 初始化连接信息
		host = config.get("server", "host")
		port = config.get("server", "port")
		self.address = (host, int(port))

		# 初始化打包头信息
		self.head_name = config.get("header", "name")
		self.head_data_len_len = int(config.get("header", "data"))
		self.head_index_len = int(config.get("header", "index"))
		self.head_time_len = int(config.get("header", "time"))

		# 初始化队列大小信息
		self.queue_size = int(config.get("receive", "queue_size"))
	
	def init_connection(self):
		try:
			self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.bind(self.address)
		except socket.error as msg:
			print(msg)
			sys.exit(1)
	
	def init_main_connection(self):
		try:
			self.main_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			self.main_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			# self.main_sock.bind(self.address_mainthread)
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
		self.init_connection()
		sock = self.sock
		# keep looping infinitely
		while True:
			if self.stopped: break
			# otherwise, ensure the queue has room in it
			if not self.Q.full():
				try:
					data, addr = sock.recvfrom(self.packer.pack_len)
					idx, ctime, raw_img = self.packer.unpack_data(data)
					line_data = numpy.frombuffer(raw_img, dtype=numpy.uint8)
					line_data = cv2.imdecode(line_data, 1).flatten()
					# self.stopped = True
					# # add the frame to the queue
					self.Q.put(FramePack(idx, ctime, line_data))
				except:
					pass
			else:
				time.sleep(0.01)  # Rest for 10ms, we have a full queue

		self.stream.release()

	def read(self):
		# frame = self.Q.get()
		# if self.Q.qsize() > self.queue_size*0.3: # self.queue_size*0.1
		# 	self.Q = Queue()
		# 	if self.Q.mutex:
		# 		self.Q.queue.clear()
		# return frame
		# print(self.Q.qsize()) # 单机运行的时候，queue的长度持续增大
		# 拥塞控制(这里可以用个算法,时间限制就写简单点)
		now = int(time.time()*1000)
		if self.Q.qsize() == 0:
			return None
			
		while self.Q.qsize() > 0:
			frame = self.Q.get()
			ctime = frame.ctime
			# select only when frametime is later than previous frame
			if ctime >= self.last_frame:
				# print("time-delay:",now - ctime," ms")
				self.last_frame = ctime
				break

		if self.Q.qsize() > self.queue_size*0.3: # self.queue_size*0.1
			self.Q = Queue()
			if self.Q.mutex:
				self.Q.queue.clear()
		return frame

	def running(self):
		return self.more() or not self.stopped

	def more(self):
		# return True if there are still frames in the queue. If stream is not stopped, try to wait a moment
		tries = 0
		while self.Q.qsize() == 0 and not self.stopped and tries < 5:
			time.sleep(0.1)
			tries += 1

		return self.Q.qsize() > 0

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
		# wait until stream resources are released (producer thread might be still grabbing frame)
		self.thread.join()


def ReceiveVideo():

	t = 0
	if t==0:
		nvs = NetVideoStream().start()
		idx_frame = nvs.packer.idx_frame
		frame = numpy.zeros(nvs.packer.frame_size_3d, dtype=numpy.uint8)
		cnt = 0
		while nvs.more():
			cnt += 1
			pack = nvs.read()
			if pack is not None:
				idx = pack.idx
				data = pack.frame
				row_start = idx*nvs.packer.piece_size
				row_end = (idx+1)*nvs.packer.piece_size
				frame[row_start:row_end] = data
				# print(data)
				if cnt == nvs.packer.frame_pieces:
					cv2.imshow("FireStreamer", frame.reshape(nvs.packer.h, nvs.packer.w, nvs.packer.d))
					cnt = 0
				nvs.require = True

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
	else:
		con = Config()
		host = con.get("server", "host")
		port = con.get("server", "port")
		address = (host, int(port))
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(address)
		bfsize = 46080
		chuncksize = 46081
		frame = numpy.zeros(bfsize*20, dtype=numpy.uint8)
		cnt = 0
		while True:
			# start = time.time()#用于计算帧率信息
			cnt += 1
			data, addr = sock.recvfrom(chuncksize)
			i = int.from_bytes(data[-1:], byteorder='big')
			line_data = numpy.frombuffer(data[:-1], dtype=numpy.uint8)
			frame[i*46080:(i+1)*46080] = line_data
			if cnt == 20:
				cv2.imshow("frame", frame.reshape(480, 640, 3))
				cnt = 0
		  
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		"""
		length = recvall(16)#获得图片文件的长度,16代表获取长度
		stringData = recvall(int(length))#根据获得的文件长度，获取图片文件
		data = numpy.frombuffer(stringData, numpy.uint8)#将获取到的字符流数据转换成1维数组
		decimg=cv2.imdecode(data,cv2.IMREAD_COLOR)#将数组解码成图像
		cv2.imshow('SERVER',decimg)#显示图像
		
		#进行下一步处理
		#。
		#。
		#。
 
        #将帧率信息回传，主要目的是测试可以双向通信
		end = time.time()
		seconds = end - start
		fps  = 1/seconds;
		s.sendto(bytes(str(int(fps)),encoding='utf-8'), address)
		k = cv2.waitKey(10)&0xff
		if k == 27:
			break
		"""
	sent =  nvs.main_sock.sendto(b"quit", client_address)
	print("The server is quitting. ")
	sock.close()
	cv2.destroyAllWindows()
 
if __name__ == '__main__':
	ReceiveVideo()