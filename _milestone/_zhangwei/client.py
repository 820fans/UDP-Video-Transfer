from threading import Thread, Lock
# from queue import Queue
# from collections import deque as Queue
import socket
import cv2
import numpy
import time
import sys
import os
from config import Config
from packer import Packer
import logging

logging.basicConfig(level=logging.DEBUG, 
                    filename='output.log',
					format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WebVideoStream:
	
	def __init__(self, src="C:\\Tools\\titan_test.mp4"):
		self.config = Config()
		self.packer = Packer()
		# initialize the file video stream along with the boolean
		# used to indicate if the thread should be stopped or not
		os.environ["OPENCV_VIDEOIO_DEBUG"] = "1"
		os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"
		encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),15]
		self.stream = cv2.VideoCapture(src)
		# while True:
		# 	if cv2.waitKey(1) & 0xFF == ord('q'):
		# 		break
		# 	ret, frame = self.stream.read()
		# 	if ret:
		# 		# print(frame.shape)
		# 		# frame = frame.reshape(self.packer.h, self.packer.w, self.packer.d)
		# 		cv2.imshow('read video data.jpg', frame)
		# self.stream.set(cv2.CAP_PROP_MODE, cv2.CAP_MODE_YUYV)
		# print(self.stream.get(cv2.CAP_PROP_FPS)) # 默认帧率30
		# self.stream.set(cv2.CAP_PROP_FPS, 20)   # cv version is 3.4.2
		self.stopped = False
		
		self.requesting = False
		self.request = False
		self.quit = False

		self.fps = 40
		self.push_sleep = 0.01
		self.push_sleep_min = 0.001
		self.push_sleep_max = 0.2

		self.piece_array = []
		self.piece_time = int(time.time()*1000)
		self.piece_fps = 40
		for i in range(self.packer.frame_pieces):
			self.piece_array.append(None)

		self.frame = numpy.zeros(self.packer.frame_size_3d, dtype=numpy.uint8)
		self.imshow = self.frame.reshape(self.packer.h, self.packer.w, self.packer.d)
		self.frame_size = 0
		self.piece_size = 0
		self.frame_pieces = 0
		self.init_config()
		self.init_connection()

		# intialize thread and lock
		self.thread = Thread(target=self.update, args=())
		self.thread.daemon = True
		
	def init_config(self):
		config = self.config
		# 初始化连接信息
		host = config.get("server", "host")
		port = config.get("server", "port")
		self.address = (host, int(port))

		# 初始化delay信息
		self.frame_delay = float(config.get("delay", "frame"))
		self.piece_delay = float(config.get("delay", "piece"))
		
		# 初始化队列大小信息
		self.queue_size = int(config.get("receive", "queue_size"))

	def init_connection(self):
		try:
			self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			# self.sock.bind(self.address)
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

			time.sleep(self.push_sleep)
			# otherwise, read the next frame from the stream
			(grabbed, frame_raw) = self.stream.read()
		
			now = int(time.time()*1000)
			for i in range(self.packer.frame_pieces):
				self.packer.pack_data(i, now, frame_raw, self.piece_array, self.piece_time, self.piece_fps)
			
			# print("pfps:", self.piece_fps)
			# now2 = int(time.time()*1000)
			# print("Time to get a frame:", (now2-now))
		return

	def Q_stuck_control(self):
		if self.piece_fps > self.packer.send_fps:
			self.push_sleep = min(self.push_sleep*2.0, self.push_sleep_max)
			return True
		if self.piece_fps < self.packer.send_fps:
			self.push_sleep = max(self.push_sleep/2.0, self.push_sleep_min)
		return False

	def get_request(self):
		if self.requesting: return

		print("waiting...")
		thread = Thread(target=self.get_request_thread, args=())
		thread.daemon = True
		thread.start()
		self.requesting = True

	def get_request_thread(self):
		while True:
			data = b''
			try:
				data, address = self.sock.recvfrom(4)
			except:
				pass
			if(data == b"get"):
				self.request = True
				break
			elif(data == b"quit"):
				self.quit = True
				break

	def read(self, i):
		return self.piece_array[i]
	
	def read_send(self, i):
		# while True:
		# 	if cv2.waitKey(1) & 0xFF == ord('q'):
		# 		break
		# start threads to recieve
		# for i in range(self.packer.frame_pieces):
			# intialize thread
		# thread = Thread(target=self.send_thread, args=(i,))
		# thread.daemon = True
		# thread.start()
		
		pack = self.piece_array[i]
		if pack is None: return
		self.sock.sendto(pack, self.address)

	def send_thread(self, i):
		pack = self.piece_array[i]
		if pack is None: return
		self.sock.sendto(pack, self.address)
		pass

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

		running = True
		while running:
			if cv2.waitKey(1) & 0xFF == ord('q'):
				running = False
				continue
			
			now = time.time()
			time.sleep(0.03)
			ctime = 0
			for i in range(wvs.packer.frame_pieces):
				wvs.read_send(i)
			now1 = time.time()
			ctime = now1 - now
			# print("frame time", ctime)
			if ctime>0:
				img = numpy.zeros((100,600,3), numpy.uint8)
				font                   = cv2.FONT_HERSHEY_SIMPLEX
				bottomLeftCornerOfText = (10,50)
				fontScale              = 1
				fontColor              = (255,255,255)
				lineType               = 2
				cv2.putText(img, 'Hello Fire! Send FPS:' + str(int(1.0/(ctime))),
					bottomLeftCornerOfText, 
					font, 
					fontScale,
					fontColor,
					lineType)
				cv2.imshow("Send clinet", img)
			# 不断地从队列里面取数据尝试
			# try:
			# 	for i in range(wvs.packer.frame_pieces):
			# 		pack = wvs.piece_array[i]
			# 		line_data = cv2.imdecode(pack, 1).flatten()
			# 		row_start = i*wvs.packer.piece_size
			# 		row_end = (i+1)*wvs.packer.piece_size
			# 		wvs.frame[row_start:row_end] = line_data

			# 	frame = wvs.frame.reshape(wvs.packer.h, wvs.packer.w, wvs.packer.d)
			# 	if frame is not None:
			# 		cv2.imshow("FireStreamer", frame)
			# except:
			# 	pass
			# now = time.time()
				# frame = wvs.read(i)
				# if frame:
				# 	# print(len(frame))
				# 	time.sleep(0.05)
				# 	sock.sendto(frame, wvs.address)
			# now1 = time.time()
			# ctime += now1 - now
			# print("frame time", ctime)
			# if ctime>0:
			# 	print("fps:", (1.0/(ctime)))


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