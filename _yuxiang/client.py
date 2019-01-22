import socket 
import cv2 
import numpy 

sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

host = socket.gethostname() # 获取本地主机名
port = 12345                # 设置端口号


# 主动初始化TCP服务器连接，。一般address的格式为元组（hostname,port），
# 如果连接出错，返回socket.error错误。
sk.connect((host, port))

capture = cv2.VideoCapture(0)
encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90] #设置编码参数


# while True
ret, frame = capture.read()
result, imgencode = cv2.imencode('.jpg', frame)
data = numpy.array(imgencode)
stringData = data.tostring()
print(type(stringData))
for i in range(0,len(stringData)):
    sk.send(stringData[i])

    
