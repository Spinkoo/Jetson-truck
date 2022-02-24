import cv2
from time import sleep
m='nvarguscamerasrc  sensor_id=0 awblock=false wbmode=1 tnr-mode=2 tnr-strength = 1  exposuretimerange=\"11000000 210000000\" gainrange=\"16 18\" ! video/x-raw(memory:NVMM), width=3840, height=2160, format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv  ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink'
#m = "nvarguscamerasrc sensor_id=0 sensor_mode = 0 wbmode=1 awblock=true gainrange=\"16 20\"  tnr-strength = 1  aelock=false ! video/x-raw(memory:NVMM), width=3840, height=2160,format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
#m ='nvarguscamerasrc tnr-mode=2 tnr-strength=1  ee-mode=2 ee-strength=1  !  video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=30/1 ! nvvidconv flip-method= 2 ! video/x-raw, format=BGRx ! videoconvert ! video/x-raw, format=BGR !  appsink'
#m = "nvarguscamerasrc sensor_id=0 wbmode=0 awblock=true  exposuretimerange=\"490000000 490000000\"  aelock=true ! video/x-raw(memory:NVMM), width=3840, height=2160,format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
#m="nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1920, height=1080, format=(string)NV12, framerate=(fraction)30/1!  nvvidconv ! 'video/x-raw(memory:NVMM),width=640,height=480' !  nvoverlaysink"
#m="nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1920, height=1080, format=(string)NV12, framerate=(fraction)30/1!  nvvidconv ! video/x-raw(memory:NVMM),width=640,height=480 !  appsink"

#m = "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)3840, height=(int)2160,format=(string)NV12, framerate=(fraction)30/1, exposuretimerange = '34000 34000', aeLock=true, ispdigitalgainrange=\"1 1\", gainrange=\"4 4\""
#m = "nvarguscamerasrc sensor-id=0 saturation=0 ! video/x-raw(memory:NVMM),width=1920,height=1080,framerate=(fraction)60/1 ! nvvidconv ! videobalance contrast=1.5 brightness=-0.3  ! nvoverlaysink !"
#m='nvarguscamerasrc  ispdigitalgainrange=\"8 8\" gainrange=\"3 3\" wbmode=0 awblock=true ! video/x-raw(memory:NVMM), width=3840, height=2160, format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! capsfilter !appsink'


cap = cv2.VideoCapture(m, cv2.CAP_GSTREAMER)

sleep(5)
_, frame = cap.read()
#cv2.normalize(frame, frame, 0, 255, cv2.NORM_MINMAX)
while True:
	_,frame=cap.read()
	cv2.imwrite('test.png',frame)
