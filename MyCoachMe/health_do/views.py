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
        # compare_result,crosscor_dict,max_index_dict = video_and_dict_pose_cross_correlation(user_video_path,professor_video_name)
        compare_result = "leg" #테스트 용
        crosscor_dict = {
            'Rarm':3.5257,'Larm':2.5622,'Relbow':1.8114,'Lelbow':2.7587,'Rwaist':4.0121,'Lwaist':2.0482, 
            'Rleg':1.7898,'Lleg':0.5642,'Rknee':2.9183,'Lknee':2.3859,  
        }
        max_index_dict = {
            'Rarm':14,'Larm':0,'Relbow':5,'Lelbow':9,'Rwaist':6,'Lwaist':4, 
            'Rleg':22 ,'Lleg':23,'Rknee':10,'Lknee':6,  
        }
        response_data = {
            'message': 'Video uploaded successfully.',
            'compare_result': compare_result,
            'crosscor_dict' : crosscor_dict, 
            'max_index_dict': max_index_dict,
            
        }
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Invalid request.'}, status=400)

def health_report(request):
    print("[health_report]")
    if request.method == 'GET' and request.GET.get('bad_body_part'):
        bad = request.GET.get('bad_body_part')
        crosscor_dict = request.GET.get('crosscor_dict') #그래프를 그리기 위해
        max_index_dict = request.GET.get('max_index_dict')
        #print(bad, crosscor_dict, max_index_dict)
        re1 = recommend_contentBased(bad)
        re2 = recommend_collaborative(bad)
        #print(re1,re2)
        return render(request,'health_do/health_report.html',{'bad':bad,'recommend-cont':re1,'recommend-coll':re2})
    else:
        return HttpResponseBadRequest('Invalid request')       