import numpy as np
import cv2
from threading import Thread
from class_canny import *
from time import time, sleep
import collections
import itertools
import os
from progress.bar import Bar
from datetime import datetime
from qr_classes import Compactor_Monitor, Bin_Monitor, data_writer
from qr_utils import *
from gps import GPS






def extract(vid_name, output_dir, gps = None):
    sleep(100)
    f = open(output_dir+'/logs.txt', 'a')
    f.write(f"Start execution was at {datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}"+'\n')
    f.close()
    print('start working on ', vid_name, ' saving in ', output_dir)
    prev_frame = None
    prev_gray = None
    Bin_M = Bin_Monitor()
    Compactor_M = Compactor_Monitor(save=output_dir + '/')
    # Capture video from camera
    # cap = cv2.VideoCapture(0)

    # Capture video from file
    cap = cv2.VideoCapture(vid_name)

    start_f = get_frame_start(output_dir)
    Compactor_M.frame_n = start_f
    data_write = data_writer()
    frame_nb = 0
    moves = 0
    stops = 0
    appears = 0
    first_ok = False
    lc = local_sim()
    error_flag = False
    while(cap.isOpened()):


        # Capture frame-by-frame
        ret, frame = cap.read()
        var = time()
        if ret == False:
            if error_flag:
              continue
            f = open(output_dir+'/logs.txt', 'a')
            f.write(f"Problem with the camera at {datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}"+'\n')
            f.close()
            error_flag = True
            continue
        error_flag = False
        if frame_nb%2==0:
          frame_nb+=1
          continue
        #bar.next()

        # check for the existence of comapctor and bin using the compactness index
        #compact, bin_ = compactor_exist(frame)


        bin_ = lc.compactor_exist(frame)
        te = cv2.resize(frame, (256, 256))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (256, 256))
        flow_gray = gray[:50, ...]
        curr_img = gray.copy()
        gray = gray[int(gray.shape[0]*0.3):, ...]

        rett, first_ok = aruco_code_detection(
            Compactor_M, te, curr_img, first_ok)

        if prev_frame is None:
            prev_frame = curr_img
            prev_gray = flow_gray
            continue
        
        flow = cv2.calcOpticalFlowFarneback(prev_gray, flow_gray,
                                            None,
                                            0.5, 3, 15, 3, 5, 1.2, 0)
        yflow = flow[..., 0]
        pos = len(yflow[yflow >= 2])
        neg = len(yflow[yflow <= -2])

        # state vector to evalute the state of the scene (existance of compactor or bin)
        Bin_M.moving_flags.appendleft(pos > 100 or neg > 100 or bin_ > 25)

        kernel = np.ones((3, 9), np.uint8)

        frame1 = cv2.absdiff(curr_img, prev_frame)
        frame1[frame1 < 10] = 0
        frame1[frame1 > 0] = 1
        moving_pixels_total = cv2.countNonZero(frame1)

        summ = np.sum(frame1, axis=1)
        all_sum = np.sum(summ[len(summ) // 2:])
        if all_sum > 2000:
            ar = np.argmax(summ)
            if ar > 180:
                compact2 = 256 - ar
            else:
                compact2 = 0
        else:
            compact2 = -1

        frame1 = cv2.morphologyEx(frame1, cv2.MORPH_OPEN, kernel)
        #compact2 = cv2.countNonZero(frame1[int(frame1.shape[0] * 0.66) :, ... ])

        Compactor_M.moving_flags.appendleft(rett > 20 or compact2 > 35)

        if sum(list(Bin_M.moving_flags)[:10]) > 7:
            Bin_M.appeared = True

        if Bin_M.moving_flags[0]:
            moves += 1

        else:
            moves = 0

        if appears > 5:
            Compactor_M.reappeared = True
        if stops > 5:
            Compactor_M.disappeared = True

        if not Compactor_M.moving_flags[0]:

            stops += 1
        else:
            stops = 0
            if Compactor_M.disappeared:
                appears += 1
            else:
                appears = 0

        if Compactor_M.reappeared:
            data_write.save_best(Compactor_M ,Bin_M, gps)

        if Bin_M.InScene():

            if Bin_M.appeared:
                data_write.save_best(Compactor_M ,Bin_M, gps)

            Compactor_M.disappeared = False
            Compactor_M.t = 0
            Compactor_M.reappeared = False
               
        else:
            if not Compactor_M.InScene() and (Bin_M.appeared or Bin_M.first_iterations):

                data_write.update_frame(Compactor_M, frame, rett, moving_pixels_total,Bin_M.first_iterations)

        Compactor_M.frame_n += 1

        prev_frame = curr_img
        prev_gray = flow_gray

        """if cv2.waitKey(1) & 0xFF == ord('q'):

            exit()"""

        total_time = time() - var
        frame_nb += 1
    f = open(output_dir+'/logs.txt', 'a')
    f.write(f"End execution was at {datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}"+'\n') 
    f.close()
    data_write.save_best(Compactor_M ,Bin_M, gps)
    # When everything done, release the capture
    cap.release()

    cv2.destroyAllWindows()




def get_local_outputdir():

    temp = glob('/home/*')
    temp = [f for f in temp if 'root' not in f]
    if len(temp) == 0:
        return '/home/ficha/data'
    path = temp[0]+'/'
    if not os.path.exists(path+'data'):
      os.makedirs(path+'data')
    return path+'data/'

def get_outputdir():
    res = os.listdir('/media/ficha')
    res = [r for r in res if 'L4T' not in r]
    return get_local_outputdir()
    
    """if len(res) == 1:
        path = '/media/ficha/'+res[0]+'/data/'
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                return path
            except:
                print('Failed creating the file')
                return get_local_outputdir() 
        return path
        
    return '/home/ficha/data'"""

def main(videos_path, formats='*.h264', output_dir='test', videos_list=None, use_camera = False, gps = None):
    from glob import glob

    if videos_list is None:
        files = glob(videos_path+formats)
    else:
        files = videos_list
    data = []
    for f in files:
        vid_name = f.split('\\')[-1]
        vid_name = vid_name.split('/')[-1]
        vid_name = vid_name.split('.')[0]

        if vid_name != '':
            data.append((f, output_dir+'/'))
           
    print(data)
    gps = GPS()
    try:
        if use_camera:
            #m='nvarguscamerasrc ! video/x-raw(memory:NVMM), width=3840, height=2160, format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink'
            #m = "nvarguscamerasrc sensor_id=0 wbmode=0 awblock=true gainrange=\"8 8\" ispdigitalgainrange=\"4 4\" exposuretimerange=\"5000000 5000000\" aelock=true ! video/x-raw(memory:NVMM), width=3840, height=2160,format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
            #m = "nvarguscamerasrc sensor_id=0 wbmode=0 awblock=true  ispdigitalgainrange=\"8 8\" exposuretimerange=\"30000 30000\" aelock=false ! video/x-raw(memory:NVMM), width=3840, height=2160,format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
            m='nvarguscamerasrc  sensor_id=0 awblock=false wbmode=1 tnr-mode=2 tnr-strength = 1  exposuretimerange=\"11000000  210000000\" gainrange=\"16 18\" ! video/x-raw(memory:NVMM), width=1920, height=1080, format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv  ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink' 
            output_dir = get_outputdir()
            extract(m, output_dir, gps)
        else :
            for f, o in data:
                i = get_outputdir()
                extract(f, i, gps)
    except Exception as  e:
        print(e)
        print('Exit code 0')
    finally:
        gps.stop = True
        print('GPS stopped')
