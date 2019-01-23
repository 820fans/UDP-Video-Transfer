from threading import Thread
from queue import Queue
import socket
import cv2
import numpy
import time
import sys
from config import Config

class FileVideoStream:
	
	def __init__(self, transform=None, queue_size=128):
		# initialize the file video stream along with the boolean
		# used to indicate if the thread should be stopped or not
		self.stream = cv2.VideoCapture(0)
		self.stream.set(cv2.CAP_PROP_MODE, cv2.CAP_MODE_YUYV)
		self.stopped = False
		self.transform = transform

		# initialize the queue used to store frames read from
		# the video file
		self.Q = Queue(maxsize=queue_size)
		# intialize thread
		self.thread = Thread(target=self.update, args=())
		self.thread.daemon = True

		self.address = None
		self.init_connection()

		#压缩参数，后面cv2.imencode将会用到，对于jpeg来说，15代表图像质量，越高代表图像质量越好为 0-100，默认95
		encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),15]

	def init_connection():
		con = Config()
		host = con.get("server", "host")
		port = con.get("server", "port")
		self.address = (host, int(port))
		try:
			sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		except socket.error as msg:
			print(msg)
			sys.exit(1)

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
				# read the next frame from the stream
				(grabbed, frame) = self.stream.read()

				# if the `grabbed` boolean is `False`, then we have reached the end of the video file
				if cv2.waitKey(1) & 0xFF == ord('q'):
					self.stopped = True
				
				# if there are transforms to be done, might as well
				# do them on producer thread before handing back to
				# consumer thread. ie. Usually the producer is so far
				# ahead of consumer that we have time to spare.
				#
				# Python is not parallel but the transform operations
				# are usually OpenCV native so release the GIL.
				#
				# Really just trying to avoid spinning up additional
				# native threads and overheads of additional
				# producer/consumer queues since this one was generally
				# idle grabbing frames.
				if self.transform:
					frame = self.transform(frame)

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

def SendVideo():
	con = Config()
	host = con.get("server", "host")
	port = con.get("server", "port")
	
	address = (host, int(port))
	
	# address = ('10.18.96.207', 8002)
	try:
		sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	except socket.error as msg:
		print(msg)
		sys.exit(1)
		
	
	capture = cv2.VideoCapture(0)
	capture.set(cv2.CAP_PROP_MODE, cv2.CAP_MODE_YUYV)
	#读取一帧图像，读取成功:ret=1 frame=读取到的一帧图像；读取失败:ret=0
	ret, frame = capture.read()
	
	
	while ret:
		#停止0.1S 防止发送过快服务的处理不过来，如果服务端的处理很多，那么应该加大这个值
		time.sleep(0.01)
		ret, frame = capture.read()
		
		for i in range(20):
		    time.sleep(0.001)
		    sock.sendto(s[i*46080:(i+1)*46080]+str.encode(str(i).zfill(2)), address)

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
			
	capture.release()
	cv2.destroyAllWindows()
	sock.close();

	
if __name__ == '__main__':
	SendVideo()
