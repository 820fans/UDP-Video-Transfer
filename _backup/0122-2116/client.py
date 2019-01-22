import socket
import cv2
import numpy
import time
import sys
 
def SendVideo():
	#建立sock连接
	#address要连接的服务器IP地址和端口号
	address = ('127.0.0.1', 8002)
	# address = ('10.18.96.207', 8002)
	try:
		#建立socket对象，参数意义见https://blog.csdn.net/rebelqsp/article/details/22109925
		#socket.AF_INET：服务器之间网络通信 
		#socket.SOCK_STREAM：流式socket , for TCP
		sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		# sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		#开启连接
		# sock.connect(address)
	except socket.error as msg:
		print(msg)
		sys.exit(1)
		
	#建立图像读取对象
	capture = cv2.VideoCapture(0)
	#读取一帧图像，读取成功:ret=1 frame=读取到的一帧图像；读取失败:ret=0
	ret, frame = capture.read()
	#压缩参数，后面cv2.imencode将会用到，对于jpeg来说，15代表图像质量，越高代表图像质量越好为 0-100，默认95
	encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),15]
	
	while ret:
		#停止0.1S 防止发送过快服务的处理不过来，如果服务端的处理很多，那么应该加大这个值
		time.sleep(0.01)
		ret, frame = capture.read()
		
		d = frame.flatten()
		s = d.tostring()
		# sock.sendto(s, address)
		for i in range(20):
		    # print(len(s[i*46080:(i+1)*46080]))
		    # print(len(str.encode(str(i).zfill(2))))
		    # print(s[i*46080:(i+1)*46080])
		    # print(str.encode(str(i).zfill(2)))
		    time.sleep(0.001)
		    sock.sendto(s[i*46080:(i+1)*46080]+str.encode(str(i).zfill(2)), address)

		# result, imgencode = cv2.imencode('.jpg', frame, encode_param)
		# data = numpy.array(imgencode)
		# stringData = data.tostring()
		
		# 先发送要发送的数据的长度
		# ljust() 方法返回一个原字符串左对齐,并使用空格填充至指定长度的新字符串
		# sock.sendto(str.encode(str(len(stringData)).ljust(16)), address)
		# 发送数据
		# sock.sendto(stringData, address);
		# 分片发送数据
		
		
		
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
	exit(404)

	
if __name__ == '__main__':
	SendVideo()
