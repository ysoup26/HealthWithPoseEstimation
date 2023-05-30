from django.shortcuts import render
from django.contrib.staticfiles import finders
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
import time
import os
from health_do.models import Train_video
from .static.health_do.python.video_and_dict_pose_cross_correlation2 import video_and_dict_pose_cross_correlation
from .static.health_do.python.content_based import recommend_contentBased
from .static.health_do.python.collaborative import recommend_collaborative
import json
import ast
#운동 비교나 추천 쪽은 파일 내에서 경로지정을 잘 해주어야 오류가 없다.

def index(request):
    return render(request,'health_do/index.html',)

#swing_waist로 테스트
def training(request):
    #video_id를 request로 받고, 그 id로 db에 접근해 영상을 가져와야함.
    if request.method == 'GET' and request.GET.get('videoId'):
        videoId = request.GET['videoId']
        video = Train_video.objects.filter(video_id=videoId)
        video_path = 'health_do/trainer_videos/'+video[0].video_name+'.mp4' #시연용
        #video_path = 'health_do/media/'+video[0].video_name+'.mp4'
        return render(request, 'health_do/training.html', {'video_path': video_path})
        #return render(request,'health_do/training.html',{'video_path':"/static/media/"+video[0].video_name+".mp4"})
    else:
        return HttpResponseBadRequest('Invalid param') 

def upload_video(request):
    print("[POST-video]")
    if request.method == 'POST' and request.FILES.get('video'):
        user_video = request.FILES['video']     #녹화된 유저 영상 데이터
        professor_video_name = request.POST['professor_video_name'] 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        now = str(int(time.time()))
        user_file_name = 'user_'+now
        print("d:",dir_path)
        user_video_path = dir_path +'/static/health_do/user_videos/'+user_file_name+'.mp4'
        user_img_path = dir_path +'/static/health_do/user_images/'+user_file_name #기본과 rec 버전 2개를 저장하기 위해 파일명까지만 함
        
        print(user_video_path,professor_video_name)
        
        #유저 영상 데이터를 .mp4파일에 작성
        with open(user_video_path, 'wb') as file:
            for chunk in user_video.chunks():
                file.write(chunk)
        
        # #유저와 전문가 운동비교
        compare_result,crosscor_dict = video_and_dict_pose_cross_correlation(user_video_path,user_img_path,professor_video_name)
        ##compare_result = "arm" #테스트 용
        ##crosscor_dict = {'arm': 6.0879, 'elbow': 4.5701, 'waist': 6.0603, 'leg': 2.354, 'knee': 5.3042}
        response_data = {
            'message': 'Video uploaded successfully.',
            'compare_result': compare_result,
            'crosscor_dict' : crosscor_dict, 
            'user_img' : user_file_name,
            'user_img_rec' : user_file_name+'_rec',
            
        }
        #print('[]:',crosscor_dict)
        #response_data_json = json.dumps(response_data) 
        #return JsonResponse(response_data_json, safe=False)
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Invalid request.'}, status=400)

def health_report(request):
    print("[health_report]")
    if request.method == 'GET' and request.GET.get('bad_body_part'):
        bad = request.GET.get('bad_body_part')
        crosscor_dict = ast.literal_eval(request.GET.get('crosscor_dict', '{}'))##request.GET.get('crosscor_dict') #그래프를 그리기 위해
        user_img = request.GET.get('user_img')
        user_img_csv = request.GET.get('user_img_rec')
        
        #print(crosscor_dict)
        #print('[test:',crosscor_dict,user_img,user_img_csv)
        
        ##테스트를 위한 임시 딕셔너리
        #bad='leg'
        #crosscor_dict = {'arm': 1.9662850522427884, 'elbow': 2.9816855583889645, 'waist': 3.843841443066744, 'leg': 5.358204912667498, 'knee': 3.196237020562813}
        percent_dict = {}

        min_value = 0  # 최소값 계산
        max_value = max(crosscor_dict.values())  # 최대값 계산
        
        #부위별 오류값을 퍼센트화: 100에 가까울 수록 가장 못한 부위(상대적표현)
        for key, value in crosscor_dict.items():
            normalized_value = (value - min_value) / (max_value - min_value)  # 최소값과 최대값 사이의 비율로 정규화
            percent = int(normalized_value * 100)  # 퍼센트 계산
            if percent == 100:
                percent_dict[key] = str(percent) +' chart--red'
            else :
                percent_dict[key] = percent

        rec1 = recommend_contentBased(bad)
        #1은 유저 아이디, 임시->후에는 실제 유저 id로 해야할것.
        #해당 운동의 bad가 csv또는 db에도 갱신이 되어야함
        rec2 = recommend_collaborative(bad,1) 
        bad = eng2kor(bad)
        
        rec1_video = Train_video.objects.filter(video_name=rec1)
        rec2_video = Train_video.objects.filter(video_name=rec2)
        
        
        return render(request,'health_do/health_report.html',{
            'bad':bad,'bad_percent':percent_dict,
            'bad_img':user_img,'bad_img_rec':user_img_csv,
            'rec_cont':rec1,'rec_coll':rec2
            ,'rec_cont_videoId':rec1_video[0].video_id,'rec_coll_videoId':rec2_video[0].video_id})
    else:
        return HttpResponseBadRequest('Invalid request')
    
def eng2kor(bad_body):
    if bad_body == "Rarm" or bad_body == "Larm":
        bad_body = "팔"
    elif bad_body == "Relbow" or bad_body == "Lelbow":
        bad_body = "팔꿈치"
    elif bad_body == "Rwaist" or bad_body == "Lwaist":
        bad_body = "허리"
    elif bad_body == "Rleg" or bad_body == "Lleg": 
        bad_body = "다리" 
    elif bad_body == "Rknee" or bad_body == "Lknee":
        bad_body = "발목"
        
    elif bad_body == "arm": 
        bad_body = "팔"
    elif bad_body == "elbow":
        bad_body = "팔꿈치"
    elif bad_body == "waist":
        bad_body = "허리"
    elif bad_body == "leg": 
        bad_body = "다리" 
    elif bad_body == "knee":
        bad_body = "발목"
    # if bad_body == "Rarm":
    #     bad_body = "팔"
    # elif bad_body == "Larm": 
    #     bad_body = "팔"
    # elif bad_body == "Relbow":
    #     bad_body = "팔꿈치"
    # elif bad_body == "Lelbow":
    #     bad_body = "팔꿈치"
    # elif bad_body == "Rwaist":
    #     bad_body = "허리"
    # elif bad_body == "Lwaist":
    #     bad_body = "허리"
    # elif bad_body == "Rleg": 
    #     bad_body = "다리" 
    # elif bad_body == "Lleg": 
    #     bad_body = "다리"
    # elif bad_body == "Rknee":
    #     bad_body = "발목"
    # elif bad_body == "Lknee":
    #     bad_body = "발목"
     
    return bad_body