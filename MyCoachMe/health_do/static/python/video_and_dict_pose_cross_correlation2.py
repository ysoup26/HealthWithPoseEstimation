'''
미리 저장해둔 전문가 영상의 각도에 대한 pickle 파일과 유저 영상을 받아 각도에 대해 cross correlation을 계산한다 그 후 틀린 부분이 표시된 영상을 출력한다. (약 10초)
(첫번째 동영상 - 전문가 , 두번째 동영상 - 유저)

딕셔너리[0] = 전문가 정보 / 딕셔너리[1] = 유저 정보
딕셔너리[0]['Rarm'] = 전문가의 오른쪽 팔에 대한 각도 정보가 프레임별로 들어있는 ndarray
딕셔너리[0]['Rarm'][0] = 전문가 영상에서 첫번째 프레임의 오른쪽 팔에 대한 각도 정보 숫자

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
from sys import platform
import pickle

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

# keypoints의 원 그릴 좌표 정해주는 함수
def get_body_center_value(keypoints, center_dict) :
    # Rarm 키가 없다면 첫번째 프레임이므로 아직 각 부위에 맞는 키가 없다.
    if 'Rarm' not in center_dict:
        center_dict['Rarm'] = [(int((keypoints[2][0]+keypoints[3][0])/2), int((keypoints[2][1]+keypoints[3][1])/2))]
        center_dict['Larm'] = [(int((keypoints[5][0]+keypoints[6][0])/2), int((keypoints[5][1]+keypoints[6][1])/2))]
        center_dict['Relbow'] = [(int((keypoints[3][0] + keypoints[4][0]) / 2), int((keypoints[3][1] + keypoints[4][1]) / 2))]
        center_dict['Lelbow'] = [(int((keypoints[6][0] + keypoints[7][0]) / 2), int((keypoints[6][1] + keypoints[7][1]) / 2))]
        center_dict['Rwaist'] = [(keypoints[9][0], keypoints[9][1])]
        center_dict['Lwaist'] = [(keypoints[12][0], keypoints[12][1])]
        center_dict['Rleg'] = [(int((keypoints[9][0] + keypoints[10][0]) / 2), int((keypoints[9][1] + keypoints[10][1]) / 2))]
        center_dict['Lleg'] = [(int((keypoints[12][0] + keypoints[13][0]) / 2), int((keypoints[12][1] + keypoints[13][1]) / 2))]
        center_dict['Rknee'] = [(int((keypoints[10][0] + keypoints[11][0]) / 2), int((keypoints[10][1] + keypoints[11][1]) / 2))]
        center_dict['Lknee'] = [(int((keypoints[13][0] + keypoints[14][0]) / 2), int((keypoints[13][1] + keypoints[14][1]) / 2))]
    # 이미 Rarm 키가 dict에 있다면 이번 값을 ndarray에 추가한다
    else:
        center_dict['Rarm'].append(
            (int((keypoints[2][0] + keypoints[3][0]) / 2), int((keypoints[2][1] + keypoints[3][1]) / 2)))
        center_dict['Larm'].append(
            (int((keypoints[5][0] + keypoints[6][0]) / 2), int((keypoints[5][1] + keypoints[6][1]) / 2)))
        center_dict['Relbow'].append(
            (int((keypoints[3][0] + keypoints[4][0]) / 2), int((keypoints[3][1] + keypoints[4][1]) / 2)))
        center_dict['Lelbow'].append(
            (int((keypoints[6][0] + keypoints[7][0]) / 2), int((keypoints[6][1] + keypoints[7][1]) / 2)))
        center_dict['Rwaist'].append((keypoints[9][0], keypoints[9][1]))
        center_dict['Lwaist'].append((keypoints[12][0], keypoints[12][1]))
        center_dict['Rleg'].append(
            (int((keypoints[9][0] + keypoints[10][0]) / 2), int((keypoints[9][1] + keypoints[10][1]) / 2)))
        center_dict['Lleg'].append(
            (int((keypoints[12][0] + keypoints[13][0]) / 2), int((keypoints[12][1] + keypoints[13][1]) / 2)))
        center_dict['Rknee'].append(
            (int((keypoints[10][0] + keypoints[11][0]) / 2), int((keypoints[10][1] + keypoints[11][1]) / 2)))
        center_dict['Lknee'].append(
            (int((keypoints[13][0] + keypoints[14][0]) / 2), int((keypoints[13][1] + keypoints[14][1]) / 2)))

    return center_dict

# =============================================================================================== #
# Cross-correlation 계산

# arr1 배열에 대해서 arr2 배열로 convolution 1d 계산을 수행한 뒤 반환하는 함수
def conv1d (arr1, arr2):
    return np.convolve(arr1, arr2, mode='valid')

# 유저 영상 일부를 잘라서 convolution 1d 연산을 수행한 뒤 그 결과 값을 반환
def cut_user_video_and_conv1d (trainer, user) :
    # 유저 영상의 맨 앞 1/10을 얻는다.
    trainer = trainer[:int(len(user) / 10) - 1]
    return conv1d(trainer, user)


# 키포인트 딕셔너리를 받아 부위별 convolution 1d를 계산한 뒤 그 값이 들어있는 딕셔너리를 반환해주는 함수
def cal_body_conv1d (dict) :
    ret_dict = {}
    # 팔
    ret_dict['Rarm'] = cut_user_video_and_conv1d(dict[0]['Rarm'], dict[1]['Rarm'])
    ret_dict['Larm'] = cut_user_video_and_conv1d(dict[0]['Larm'], dict[1]['Larm'])

    # 팔꿈치
    ret_dict['Relbow'] = cut_user_video_and_conv1d(dict[0]['Relbow'], dict[1]['Relbow'])
    ret_dict['Lelbow'] = cut_user_video_and_conv1d(dict[0]['Lelbow'], dict[1]['Lelbow'])

    # 허리
    ret_dict['Rwaist'] = cut_user_video_and_conv1d(dict[0]['Rwaist'], dict[1]['Rwaist'])
    ret_dict['Lwaist'] = cut_user_video_and_conv1d(dict[0]['Lwaist'], dict[1]['Lwaist'])

    # 다리(허벅지)
    ret_dict['Rleg'] = cut_user_video_and_conv1d(dict[0]['Rleg'], dict[1]['Rleg'])
    ret_dict['Lleg'] = cut_user_video_and_conv1d(dict[0]['Lleg'], dict[1]['Lleg'])

    # 무릎
    ret_dict['Rknee'] = cut_user_video_and_conv1d(dict[0]['Rknee'], dict[1]['Rknee'])
    ret_dict['Lknee'] = cut_user_video_and_conv1d(dict[0]['Lknee'], dict[1]['Lknee'])

    return ret_dict

# 차이를 계산한 뒤 차이 배열과 가장 차이가 큰 부분의 시작 인덱스를 리턴한다.
def cal_difference (arr1, arr2):
    # 두 배열의 길이가 다르면 긴 배열의 끝을 자른다.
    if len(arr1) > len(arr2):
        arr1 = arr1[:len(arr2)]
    elif len(arr1) < len(arr2):
        arr2 = arr2[:len(arr1)]

    difference = arr1 - arr2

    # 가장 많이 틀린 부분 시작 인덱스
    offset = int(len(arr2)/10)
    max = 0
    max_index = 0
    for i in range(int(len(arr2)-offset)):
        sum = np.sum(difference[i:i+offset])
        if sum > max:
            max = sum
            max_index = i

    diff_mean = np.abs(np.mean(difference))
    return diff_mean, max_index


# Cross correlation 계산 후 차이의 평균값과 최대 차이 부분의 인덱스 리턴
def cal_cross_corr (dict):
    diff_dict = {}
    conv_dict = cal_body_conv1d(dict)
    conv_sum_arr = [conv_dict['Rarm'][i] + conv_dict['Larm'][i] + conv_dict['Relbow'][i] + conv_dict['Lelbow'][i]
                    + conv_dict['Rwaist'][i] + conv_dict['Lwaist'][i] + conv_dict['Rleg'][i] + conv_dict['Lleg'][i]
                    + conv_dict['Rknee'][i] + conv_dict['Lknee'][i]
                    for i in range(len(conv_dict['Rarm']))]
    ind = np.argmax(conv_sum_arr)


    if ind == len(dict[0]['Rarm'])-1 :
        ind = 0

    # 유저 영상 각도 배열의 앞 부분을 자르기
    dict[1]['Rarm'] = dict[1]['Rarm'][ind:]
    dict[1]['Larm'] = dict[1]['Larm'][ind:]
    dict[1]['Relbow'] = dict[1]['Relbow'][ind:]
    dict[1]['Lelbow'] = dict[1]['Lelbow'][ind:]
    dict[1]['Rwaist'] = dict[1]['Rwaist'][ind:]
    dict[1]['Lwaist'] = dict[1]['Lwaist'][ind:]
    dict[1]['Rleg'] = dict[1]['Rleg'][ind:]
    dict[1]['Lleg'] = dict[1]['Lleg'][ind:]
    dict[1]['Rknee'] = dict[1]['Rknee'][ind:]
    dict[1]['Lknee'] = dict[1]['Lknee'][ind:]

    # 차이 계산 후 평균값 출력하기
    max_index_dict = {}
    diff_dict['Rarm'], max_index_dict['Rarm'] = cal_difference(dict[0]['Rarm'], dict[1]['Rarm'])
    diff_dict['Larm'], max_index_dict['Larm'] = cal_difference(dict[0]['Larm'], dict[1]['Larm'])
    diff_dict['Relbow'], max_index_dict['Relbow'] = cal_difference(dict[0]['Relbow'], dict[1]['Relbow'])
    diff_dict['Lelbow'], max_index_dict['Lelbow'] = cal_difference(dict[0]['Lelbow'], dict[1]['Lelbow'])
    diff_dict['Rwaist'], max_index_dict['Rwaist'] = cal_difference(dict[0]['Rwaist'], dict[1]['Rwaist'])
    diff_dict['Lwaist'], max_index_dict['Lwaist'] = cal_difference(dict[0]['Lwaist'], dict[1]['Lwaist'])
    diff_dict['Rleg'], max_index_dict['Rleg'] = cal_difference(dict[0]['Rleg'], dict[1]['Rleg'])
    diff_dict['Lleg'], max_index_dict['Lleg'] = cal_difference(dict[0]['Lleg'], dict[1]['Lleg'])
    diff_dict['Rknee'], max_index_dict['Rknee'] = cal_difference(dict[0]['Rknee'], dict[1]['Rknee'])
    diff_dict['Lknee'], max_index_dict['Lknee'] = cal_difference(dict[0]['Lknee'], dict[1]['Lknee'])

    return diff_dict, max_index_dict

# ===================================================================================================== #
# 메인
def video_and_dict_pose_cross_correlation(user_video_path,professor_video_name):
    try:
        # Import Openpose (Windows/Ubuntu/OSX)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        openpose_path = dir_path + "/../../../openpose/python"
        print("dir_path:",dir_path)
        print("openpose_path:",openpose_path)
        try:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(openpose_path + '/../bin/python/openpose/Release');
            os.environ['PATH']  = os.environ['PATH'] + ';' + openpose_path + '/../x64/Release;' +  openpose_path + '/../bin;'
            import pyopenpose as op
        except ImportError as e:
            print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
            raise e
        start = time.time()
        # image paths
        
        # 이미지 읽기
        user_video = cv2.VideoCapture(user_video_path)

        trainer_pickle = os.path.join(dir_path, '../trainer_videos/angle_dict', professor_video_name + '.pickle')
        print("pickle: ",trainer_pickle)
        
        # Custom Params (refer to include/openpose/flags.hpp for more parameters)
        params = dict()
        params["model_folder"] = openpose_path + "/../models/"

        # Starting OpenPose
        print("[Openpose start]")
        opWrapper = op.WrapperPython()
        opWrapper.configure(params)
        opWrapper.start()

        # Get body parts and pose pairs from openpose library (refer to openpose/src/openpose/pose/poseParameters.cpp for more parameters)
        BODY_PARTS = op.getPoseBodyPartMapping(op.BODY_25)
        POSE_PAIRS = op.getPosePartPairs(op.BODY_25)
        index_names = copy.deepcopy(BODY_PARTS)
        index_names.pop(25)



        angles_dict = {0: {}, 1: {}}       # 각도를 저장하는 dict
        center_dict = {}  # 점 그릴 중심 좌표 저장하는 dict

        # pickle 읽어서 angles_dict[0]에 저장
        with open(trainer_pickle, 'rb') as f:
            angles_dict[0] = pickle.load(f)

        # Processing
        # angles_dict[1]에 유저의 각도 정보를 저장한다.
        print("[user_video_read start]")
        while True :
            ret, frameToProcess = user_video.read()

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

            # openpose 연산
            datum = op.Datum()
            datum.cvInputData = frameToProcess
            opWrapper.emplaceAndPop(op.VectorDatum([datum]))
            network_output = datum.poseKeypoints
            human = network_output[0]
            angles_dict[1] = get_body_angle(human, angles_dict[1])
            # 점 찍을 좌표 구해두기
            center_dict = get_body_center_value(human, center_dict)


        print("\n")

        #print(angles_dict)
        #부위별 차이의 평균, 부위별 최대 차이의 인덱스
        crosscor_dict, max_index_dict = cal_cross_corr(angles_dict)
        
        new_crosscor_dict = {}
        #부위별 차이 딕셔너리 LR 통합
        for key, value in crosscor_dict.items():
            new_key = key[1:]  # R 또는 L을 제외한 부분을 새로운 키로 사용
            if new_key in new_crosscor_dict:
                new_crosscor_dict[new_key] += value
            else:
                new_crosscor_dict[new_key] = value
        
        #print("\n")
        print(new_crosscor_dict)

        end = time.time()
        print("Total time: " + str(end - start) + " seconds")

        # 가장 많이 틀린 부분 찾기
        max_body_key = max(new_crosscor_dict, key=new_crosscor_dict.get)
        end_frame = max_index_dict[max_body_key] + 300

        #틀린 부분하나.
        print(max_body_key)

        return max_body_key,new_crosscor_dict
        # 영상 틀어주기
        # center_dict[max_body_key] = center_dict[max_body_key][max_index_dict[max_body_key]:]
        # user_video.set(cv2.CAP_PROP_POS_FRAMES, max_index_dict[max_body_key])
        # i=0
        # while user_video.isOpened() and user_video.get(cv2.CAP_PROP_POS_FRAMES) < end_frame:
        #     # print("while in")
        #     ret, frame = user_video.read()

        #     if not ret:
        #         print("not ret")
        #         break

        #     if frame.shape[0] != 800:
        #         height = 800
        #         aspect_ratio = float(height) / frame.shape[0]
        #         dsize = (int(frame.shape[1] * aspect_ratio), height)
        #         frame = cv2.resize(frame, dsize, interpolation=cv2.INTER_AREA)


        #     r = 15
        #     c = (0, 0, 255)
        #     cv2.circle(frame, center_dict[max_body_key][i], r, c, -1)
        #     i = i+1
        #     #cv2.imshow('wrong pose', frame)
        #     if cv2.waitKey(25) & 0xFF == ord('q'):
        #         print("quit")
        #         break


        # user_video.release()
        
        #cv2.destroyAllWindows()

        #end = time.time()
        #print("OpenPose demo successfully finished. Total time: " + str(end - start) + " seconds")

    except Exception as e:
        print(e)
    
    return 0