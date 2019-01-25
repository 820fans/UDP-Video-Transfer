
import cv2 
cap = cv2.VideoCapture(0)
cv2.namedWindow("test")
while(True):
    result, frame = cap.read()
    cv2.imshow('test',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
