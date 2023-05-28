import sys
import cv2
import os
import math
import numpy as np
import time
from sys import platform
import pickle

import copy
import pandas as pd
from itertools import zip_longest

max_index_dict = {
    'Rarm':14,'Larm':0,'Relbow':5,'Lelbow':9,'Rwaist':6,'Lwaist':4, 
    'Rleg':22 ,'Lleg':23,'Rknee':10,'Lknee':6,  
}
max_body_key='Rarm'

dir_path = os.path.dirname(os.path.realpath(__file__))

user_video_path = dir_path+'/../media/backkick.mp4'
user_video = cv2.VideoCapture(user_video_path)

end_frame = max_index_dict[max_body_key] + 300

print(user_video_path)
#center_dict[max_body_key] = center_dict[max_body_key][max_index_dict[max_body_key]:]
user_video.set(cv2.CAP_PROP_POS_FRAMES, max_index_dict[max_body_key])
i=0
while user_video.isOpened() and user_video.get(cv2.CAP_PROP_POS_FRAMES) < end_frame:
    # print("while in")
    ret, frame = user_video.read()

    if not ret:
        print("not ret")
        break

    if frame.shape[0] != 800:
        height = 800
        aspect_ratio = float(height) / frame.shape[0]
        dsize = (int(frame.shape[1] * aspect_ratio), height)
        frame = cv2.resize(frame, dsize, interpolation=cv2.INTER_AREA)


    r = 15
    c = (0, 0, 255)
    #cv2.circle(frame, center_dict[max_body_key][i], r, c, -1)
    i = i+1
    cv2.imshow('wrong pose', frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        print("quit")
    break


user_video.release()
        
cv2.destroyAllWindows()