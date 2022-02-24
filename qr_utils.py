import numpy as np
import cv2
import os
from cv2 import aruco
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters_create()


def get_frame_start(path):
    from glob import glob

    c = glob(path+'/*.json')
    if len(c) == 0:
        return 0
    c = [i.split('/')[-1].split('\\')[-1] for i in c]
    c = sorted([int(i.split('.')[0]) for i in c])
    
    return np.max(c)


def compactor_exists(gray):

    corners, ids, rejectedImgPoints = aruco.detectMarkers(
        gray, aruco_dict, parameters=parameters)
    if len(corners) > 0:

        idss = np.array(ids).reshape(-1)
        idss = np.where(idss == 6)

        if len(idss[0]) == 0:
            idss = [[0]]

        return np.squeeze(corners[idss[0][0]]).astype('int')

    return None


def get_bbox(bbox):
    xmin = np.min(bbox[:, 0])
    ymin = np.min(bbox[:, 1])
    xmax = np.max(bbox[:, 0])
    ymax = np.max(bbox[:, 1])
    return xmin, ymin, xmax, ymax


def aruco_code_detection(Compactor_M, frame, curr_img, first_ok):

    if Compactor_M.marker is not None:
        ok, bbox = Compactor_M.tracker.update(frame)

        if ok:
            first_ok = True

            p1 = (int(bbox[0]), int(bbox[1]))

            rett = 256 - 20 - p1[1]
            if rett < -1:
                rett = 0

        else:
            rett = -1
            first_ok = False

    else:
        ok = False
        rett = -1
    if not ok:
        compactor_y = compactor_exists(curr_img)
        if compactor_y is not None:
            xmin, ymin, xmax, ymax = get_bbox(compactor_y)

            Compactor_M.marker = curr_img[ymin - 50:ymin+5, xmin:xmin+20]

            if not first_ok:
                Compactor_M.tracker = cv2.TrackerKCF_create()
                Compactor_M.tracker.init(frame, (xmin, ymin - 10, 20, 20))

            rett = 256 - ymin + 10

        else:
            rett = -1
    return rett, first_ok


def create_output_folder(path):
    try:
        os.mkdir(path)
        return True
    except OSError:
        return False
