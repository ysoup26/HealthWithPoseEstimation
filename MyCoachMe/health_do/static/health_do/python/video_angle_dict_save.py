'''
전문가 동영상이 들어있는 path를 입력하면 각도를 계산 후 dict로 저장하는 프로그램

writer : 륜경
'''


# From Python
# It requires OpenCV installed for Python
import sys
import cv2
import os
import math
import numpy as np
import time
import pickle
from sys import platform

import copy
import pandas as pd
from itertools import zip_longest

# 두 직선의 각 좌표가 전해지면 두 직선이 이루는 각을 계산해서 반환해주는 함수.
def get_angle(x1, y1, x2, y2, cx, cy) :
    return float(math.atan2(y2-cy, x2-cx) - math.atan2(y1-cy, x1-cx))


'''
keypoints[부위 번호][x,y,confidence]
[x, y, confidence]
0 - x좌표
1 - y좌표
3 - confidence
'''
# 키포인트 데이터와 저장하는 딕셔너리를 전달받아서 각 부위에 대한 각도를 계산한 뒤 반환해주는 함수.
def get_body_angle(keypoints, dict):

    # Rarm 키가 없다면 첫번째 프레임이므로 아직 각 부위에 맞는 키가 없다.
    if 'Rarm' not in dict:
        #팔
        dict['Rarm'] = np.array(get_angle(keypoints[1][0], keypoints[1][1],
                                       keypoints[3][0], keypoints[3][1],
                                       keypoints[2][0], keypoints[2][1]))
        dict['Larm'] = np.array(get_angle(keypoints[1][0], keypoints[1][1],
                                       keypoints[6][0], keypoints[6][1],
                                       keypoints[5][0], keypoints[5][1]))
        #팔꿈치
        dict['Relbow'] = np.array(get_angle(keypoints[2][0], keypoints[2][1],
                                       keypoints[4][0], keypoints[4][1],
                                       keypoints[3][0], keypoints[3][1]))
        dict['Lelbow'] = np.array(get_angle(keypoints[5][0], keypoints[5][1],
                                         keypoints[7][0], keypoints[7][1],
                                         keypoints[6][0], keypoints[6][1]))
        #허리
        dict['Rwaist'] = np.array(get_angle(keypoints[1][0], keypoints[1][1],
                                         keypoints[9][0], keypoints[9][1],
                                         keypoints[8][0], keypoints[8][1]))
        dict['Lwaist'] = np.array(get_angle(keypoints[1][0], keypoints[1][1],
                                         keypoints[12][0], keypoints[12][1],
                                         keypoints[8][0], keypoints[8][1]))
        #다리(허벅지)
        dict['Rleg'] = np.array(get_angle(keypoints[8][0], keypoints[8][1],
                                         keypoints[10][0], keypoints[10][1],
                                         keypoints[9][0], keypoints[9][1]))
        dict['Lleg'] = np.array(get_angle(keypoints[8][0], keypoints[8][1],
                                         keypoints[13][0], keypoints[13][1],
                                         keypoints[12][0], keypoints[12][1]))
        #무릎
        dict['Rknee'] = np.array(get_angle(keypoints[9][0], keypoints[9][1],
                                         keypoints[11][0], keypoints[11][1],
                                         keypoints[10][0], keypoints[10][1]))
        dict['Lknee'] = np.array(get_angle(keypoints[12][0], keypoints[12][1],
                                         keypoints[14][0], keypoints[14][1],
                                         keypoints[13][0], keypoints[13][1]))
    # 이미 Rarm 키가 dict에 있다면 이번 값을 ndarray에 추가한다.
    else:
        # 팔
        dict['Rarm'] = np.append(dict['Rarm'], get_angle(keypoints[1][0], keypoints[1][1],
                                          keypoints[3][0], keypoints[3][1],
                                          keypoints[2][0], keypoints[2][1]))
        dict['Larm'] = np.append(dict['Larm'], get_angle(keypoints[1][0], keypoints[1][1],
                                          keypoints[6][0], keypoints[6][1],
                                          keypoints[5][0], keypoints[5][1]))
        # 팔꿈치
        dict['Relbow'] = np.append(dict['Relbow'], get_angle(keypoints[2][0], keypoints[2][1],
                                            keypoints[4][0], keypoints[4][1],
                                            keypoints[3][0], keypoints[3][1]))
        dict['Lelbow'] = np.append(dict['Lelbow'], get_angle(keypoints[5][0], keypoints[5][1],
                                            keypoints[7][0], keypoints[7][1],
                                            keypoints[6][0], keypoints[6][1]))
        # 허리
        dict['Rwaist'] = np.append(dict['Rwaist'], get_angle(keypoints[1][0], keypoints[1][1],
                                            keypoints[9][0], keypoints[9][1],
                                            keypoints[8][0], keypoints[8][1]))
        dict['Lwaist'] = np.append(dict['Lwaist'], get_angle(keypoints[1][0], keypoints[1][1],
                                            keypoints[12][0], keypoints[12][1],
                                            keypoints[8][0], keypoints[8][1]))
        # 다리(허벅지)
        dict['Rleg'] = np.append(dict['Rleg'], get_angle(keypoints[8][0], keypoints[8][1],
                                          keypoints[10][0], keypoints[10][1],
                                          keypoints[9][0], keypoints[9][1]))
        dict['Lleg'] = np.append(dict['Lleg'], get_angle(keypoints[8][0], keypoints[8][1],
                                          keypoints[13][0], keypoints[13][1],
                                          keypoints[12][0], keypoints[12][1]))
        # 무릎
        dict['Rknee'] = np.append(dict['Rknee'], get_angle(keypoints[9][0], keypoints[9][1],
                                           keypoints[11][0], keypoints[11][1],
                                           keypoints[10][0], keypoints[10][1]))
        dict['Lknee'] = np.append(dict['Lknee'], get_angle(keypoints[12][0], keypoints[12][1],
                                           keypoints[14][0], keypoints[14][1],
                                           keypoints[13][0], keypoints[13][1]))

    return dict


# ===================================================================================================== #
# 메인

try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../openpose/python"
    print("dir_path:",dir_path)
    try:
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append(dir_path + '/../bin/python/openpose/Release');
        os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../x64/Release;' +  dir_path + '/../bin;'
        import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e
    start = time.time()
    # video path
    trainer_video_path = '../trainer_videos'
    files = os.listdir(trainer_video_path)
    video_files = [f for f in files if f.endswith(('.mp4', '.avi', '.mov'))]
    print(video_files)
    #video_files = ['../trainer_videos/backkickstep_and_low.mp4']

    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = "../models/"

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()

    # Get body parts and pose pairs from openpose library (refer to openpose/src/openpose/pose/poseParameters.cpp for more parameters)
    BODY_PARTS = op.getPoseBodyPartMapping(op.BODY_25)
    POSE_PAIRS = op.getPosePartPairs(op.BODY_25)
    index_names = copy.deepcopy(BODY_PARTS)
    index_names.pop(25)

    angles_dict = {}                      # 각도를 저장하는 dict
    # user_keypoints = np.zeros((25, 3))


    # Process images
    for video_str in video_files:
        print(video_str)
        video = cv2.VideoCapture('../trainer_videos/' + video_str)
        while True :
            ret, frameToProcess = video.read()

            # 연산 상황을 알려주는 출력
            print(">", end='')

            # 읽은 프레임이 없으면(=영상 끝나면) 루프 종료
            if not ret:
                break

            # 이미지 높이를 800으로 바꾸고, 너비도 그에 맞추어 변경
            if frameToProcess.shape[0] != 800 :
                height = 800
                aspect_ratio = float(height) / frameToProcess.shape[0]
                dsize = (int(frameToProcess.shape[1] * aspect_ratio), height)
                frameToProcess = cv2.resize(frameToProcess, dsize, interpolation=cv2.INTER_AREA)
            datum = op.Datum()
            datum.cvInputData = frameToProcess
            opWrapper.emplaceAndPop(op.VectorDatum([datum]))
            # 키포인트 저장
            network_output = datum.poseKeypoints
            human = network_output[0]
            # 각도 계산 및 저장
            angles_dict = get_body_angle(human, angles_dict)
        # anlges_dict 딕셔너리를 컴퓨터에 저장
        save_directory = "../trainer_videos/angle_npy/"+video_str
        save_directory = save_directory.replace(".mp4", ".pickle")
        with open(save_directory, 'wb') as f:
            pickle.dump(angles_dict, f)
        video.release()
        print("\n")


    end = time.time()
    print("Total time: " + str(end - start) + " seconds")

    #end = time.time()
    #print("OpenPose demo successfully finished. Total time: " + str(end - start) + " seconds")


except Exception as e:
    print(e)
    sys.exit(-1)