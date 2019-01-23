import socket
import time
import cv2
import numpy
from config import Config

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