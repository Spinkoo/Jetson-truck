from collections import deque
import numpy as np
import cv2
import base64
import json
from datetime import datetime
from post_office import office
class Compactor_Monitor(object):
    def __init__(self, id_im=0, save='test/'):
        self.frame = None
        self.id = id_im
        self.path_save = save
        self.reset_flags()
        self.reinit()
        self.frame_save = 0
        self.frame_n = 0
        self.disappeared = False
        self.reappeared = False
        self.f_done = False
        self.marker = None
        self.tracker = None


    def reinit(self):
        self.moving_pixels = 999999
        self.compactor_pixels = 999999
        self.t = 0
    def reset_flags(self):
        self.moving_flags =  deque([1]*5,maxlen=5)
    def InScene(self):
        return np.count_nonzero(self.moving_flags) > 0

class Bin_Monitor(object):
    def __init__(self):
        self.moving_flags = deque([0]*30, maxlen=30)
        self.first_iterations = True
        self.appeared = False

    def InScene(self):

        return (np.sum(self.moving_flags) > 8) or (sum(list(self.moving_flags)[:12]) > 0)


class data_writer(object):
    def __init__(self, ):
        self.post_office = office()

        #update the frame that will be saved
    def update_frame(self, Compactor_M, frame,m, m_pixels, first):

        if (m <= Compactor_M.compactor_pixels) and (not Compactor_M.reappeared or first):
            
            if m_pixels < Compactor_M.moving_pixels:
                Compactor_M.compactor_pixels = m
                Compactor_M.moving_pixels = m_pixels
                Compactor_M.frame = frame
            Compactor_M.compactor_pixels = m
            
        else :
            Compactor_M.t = Compactor_M.t - 1
            if Compactor_M.t < 0:
                Compactor_M.reinit()
        return False


    # save best frame
    def encode_data(self, frame, gps,n, path):
        string = base64.b64encode(cv2.imencode('.png', frame)[1]).decode()
        dict = {
            'img': string,
             'coord' : gps._gpsData
        }
        with open(f'{path}/{n}.json', 'w') as outfile:
            json.dump(dict, outfile, ensure_ascii=False, indent=4)
    def save_data(self, frame, gps, n, path):
        print(gps.lat, gps.lon)
        cv2.imwrite(f'{path}/{n}.jpg', frame)
        dict = {
                'fpath': f'{path}/{n}.jpg',
                'time_stamp' : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'latitude' : gps.lat,
                'longitude' : gps.lon
               }
        with open(f'{path}/{n}.json', 'w') as outfile:
            json.dump(dict, outfile, ensure_ascii=False, indent=4)
        self.post_office.push_data(f'{path}/{n}.json')

    def save_best(self, Compactor_M, Bin_M, gps):
        if Compactor_M.frame is not None: 
            if Compactor_M.frame_n - Compactor_M.frame_save < 10 :
                Compactor_M.frame = None
                return

            #cv2.imwrite(Compactor_M.path_save+str(Compactor_M.frame_n)+'_1.png', Compactor_M.frame)
            #self.encode_data(Compactor_M.frame, gps, Compactor_M.frame_n, Compactor_M.path_save)
            self.save_data(Compactor_M.frame, gps, Compactor_M.frame_n, Compactor_M.path_save)
            Compactor_M.id += 1 
            Compactor_M.reinit()
            Compactor_M.reset_flags()
            Compactor_M.frame_save = Compactor_M.frame_n
            Compactor_M.f_done = False
            Bin_M.appeared = False
            Bin_M.first_iterations = False
