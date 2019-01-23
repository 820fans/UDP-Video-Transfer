import socket
import time
import cv2
import numpy
from config import Config


class NetVideoStream:
	def __init__(self, path, queue_size=128):
		# initialize the file video stream along with the boolean
		# used to indicate if the thread should be stopped or not
		self.stream = cv2.VideoCapture(path)
		self.stopped = False

		# initialize the queue used to store frames read from
		# the video file
		self.Q = Queue(maxsize=queue_size)
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
		self.chuncksize = piece_size+1

		# 初始化连接信息
		host = config.get("server", "host")
		port = config.get("server", "port")
		self.address = (host, int(port))

		# 初始化打包头信息
		self.head_name = config.get("header", "name")
		self.head_data_len_len = int(config.get("header", "data"))
		self.head_index_len = int(config.get("header", "index"))
		self.head_time_len = int(config.get("header", "time"))
	
	def init_connection(self):
		try:
			self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			self.sock.bind(address)
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
		# keep looping infinitely
		while True:
			# if the thread indicator variable is set, stop the
			# thread
			if self.stopped:
				break

			# otherwise, ensure the queue has room in it
			if not self.Q.full():
				# read the next frame from the file
				(grabbed, frame) = self.stream.read()

				# add the frame to the queue
				self.Q.put(frame)
			else:
				time.sleep(0.1)  # Rest for 10ms, we have a full queue

		self.stream.release()

	def read(self):
		# return next frame in the queue
		return self.Q.get()

	# Insufficient to have consumer use while(more()) which does
	# not take into account if the producer has reached end of
	# file stream.
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
	con = Config()
	host = con.get("server", "host")
	port = con.get("server", "port")
	
	address = (host, int(port))
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(address)

	# UDP不需要建立连接
	bfsize = 46080
	chuncksize = 46081
	
	frame = numpy.zeros(bfsize*20, dtype=numpy.uint8)
	cnt = 0
	s = b''
	while 1:
		# start = time.time()#用于计算帧率信息
		cnt += 1
		data, addr = sock.recvfrom(chuncksize)
		i = int.from_bytes(data[-1:], byteorder='big')
		line_data = numpy.frombuffer(data[:-1], dtype=numpy.uint8)
		frame[i*46080:(i+1)*46080] = line_data
		if cnt == 20:
		    cv2.imshow("frame", frame.reshape(480, 640, 3))
		    cnt = 0
		#print(cnt)
		
		
		# s += data[:-2]
		# if len(s) == (46080*20):
		    # frame = numpy.fromstring(s, dtype=numpy.uint8)
		    # frame = frame.reshape(480, 640,3)
		    # cv2.imshow("frame",frame)

		    # s = b''
		  
		#key = cv2.waitKey(1)
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
	sock.close()
	cv2.destroyAllWindows()
 
if __name__ == '__main__':
	ReceiveVideo()