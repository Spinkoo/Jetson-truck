import sys
import cv2

def read_cam():
    for j in range(1, 22):
        for i in range(13000, 22000, 300):
            m = f'nvarguscamerasrc sensor_id=0 wbmode=1 tnr-mode = 2 exposuretimerange=\"{i} {i}\" gainrange=\"{j} {j}\" aelock=true ! video/x-raw(memory:NVMM), width=3280, height=2464, format=(string)NV12, framerate=30/1 ! nvvidconv flip-method=1 ! video/x-raw, width=960, height=616, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink wait-on-eos=false max-buffers=1 drop=True'

            cap = cv2.VideoCapture(m, cv2.CAP_GSTREAMER)
            print(f'making {i}')
            if cap.isOpened():
                ret_val, img = cap.read()
                if img is None:
                    cap.release()
                    continue
                cv2.imwrite(f'test/test{i}_{j}.png', img)
            else:
             print("camera open failed")
            cap.release()


if __name__ == '__main__':
    read_cam()
