from django.shortcuts import render
from django.contrib.staticfiles import finders
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
import time
import os
from health_do.models import Train_video
from .static.python.video_and_dict_pose_cross_correlation2 import video_and_dict_pose_cross_correlation
from .static.python.content_based import recommend_contentBased
from .static.python.collaborative import recommend_collaborative

#운동 비교나 추천 쪽은 파일 내에서 경로지정을 잘 해주어야 오류가 없다.

def index(request):
    return render(request,'health_do/index.html',)

def health_do(request):
    #video_id를 request로 받고, 그 id로 db에 접근해 영상을 가져와야함.
    if request.method == 'GET' and request.GET.get('videoId'):
        videoId = request.GET['videoId']
        #print("videoId",videoId)
        video = Train_video.objects.filter(video_id=videoId)
        #print(video,video[0].video_id,video[0].video_name)
        return render(request,'health_do/health_do.html',{'video_path':"/static/media/"+video[0].video_name+".mp4"})
    else:
        return HttpResponseBadRequest('Invalid param') 

def upload_video(request):
    print("[POST-video]")
    if request.method == 'POST' and request.FILES.get('video'):
        user_video = request.FILES['video']     #녹화된 유저 영상 데이터
        professor_video_name = request.POST['professor_video_name'] 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        now = int(time.time())
        user_video_path = dir_path +'/static/user_videos/user_'+str(now)+'.mp4'
        
        print(user_video_path,professor_video_name)
        
        #유저 영상 데이터를 .mp4파일에 작성
        # with open(user_video_path, 'wb') as file:
        #     for chunk in user_video.chunks():
        #         file.write(chunk)
        
        # #유저와 전문가 운동비교
        # compare_result,crosscor_dict = video_and_dict_pose_cross_correlation(user_video_path,professor_video_name)
        compare_result = "arm" #테스트 용
        # crosscor_dict = {
        #     'Rarm':3.5257,'Larm':2.5622,'Relbow':1.8114,'Lelbow':2.7587,'Rwaist':4.0121,'Lwaist':2.0482, 
        #     'Rleg':1.7898,'Lleg':0.5642,'Rknee':2.9183,'Lknee':2.3859,  
        # }
        crosscor_dict = {'arm': 6.0879, 'elbow': 4.5701, 'waist': 6.0603, 'leg': 2.354, 'knee': 5.3042}
        response_data = {
            'message': 'Video uploaded successfully.',
            'compare_result': compare_result,
            'crosscor_dict' : crosscor_dict, 
            
        }
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Invalid request.'}, status=400)

def health_report(request):
    print("[health_report]")
    if request.method == 'GET' and request.GET.get('bad_body_part'):
        bad = request.GET.get('bad_body_part')
        crosscor_dict = request.GET.get('crosscor_dict') #그래프를 그리기 위해
        
        #테스트를 위한 임시 딕셔너리
        # crosscor_dict = {
        #     'Rarm':3.5257,'Larm':2.5622,'Relbow':1.8114,'Lelbow':2.7587,'Rwaist':4.0121,'Lwaist':2.0482, 
        #     'Rleg':1.7898,'Lleg':0.5642,'Rknee':2.9183,'Lknee':2.3859,  
        # }
        # max_index_dict = {
        #     'Rarm':14,'Larm':0,'Relbow':5,'Lelbow':9,'Rwaist':6,'Lwaist':4, 
        #     'Rleg':22 ,'Lleg':23,'Rknee':10,'Lknee':6,  
        # }
        crosscor_dict = {'arm': 6.0879, 'elbow': 4.5701, 'waist': 6.0603, 'leg': 2.354, 'knee': 5.3042}
        #max_index_dict = {'arm': 14, 'elbow': 14, 'waist': 10, 'leg': 45, 'knee': 16}
        #print("출력:",bad, crosscor_dict, max_index_dict)
        
        percent_dict = {}

        min_value = 0  # 최소값 계산
        max_value = max(crosscor_dict.values())  # 최대값 계산
        
        #부위별 오류값을 퍼센트화: 100에 가까울 수록 가장 못한 부위(상대적표현)
        for key, value in crosscor_dict.items():
            normalized_value = (value - min_value) / (max_value - min_value)  # 최소값과 최대값 사이의 비율로 정규화
            percent = int(normalized_value * 100)  # 퍼센트 계산
            percent_dict[key] = percent
        print('dict:',percent_dict)

        re1 = recommend_contentBased(bad)
        re2 = recommend_collaborative(bad)
        bad = eng2kor(bad)
        print(re1,re2)
        
        return render(request,'health_do/health_report.html',{'bad':bad,'bad_percent':percent_dict,'recommend_cont':re1,'recommend_coll':re2})
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