from django.shortcuts import render
from django.contrib.staticfiles import finders
import subprocess
from .static.python.video_and_dict_pose_cross_correlation2 import video_and_dict_pose_cross_correlation
from .static.python.content_based import recommend_contentBased
from .static.python.collaborative import recommend_collaborative

# Create your views here.

def index(request):
    return render(request,'health_do/index.html')

def health_do(request):
    #video_id를 request로 받고, 그 id로 db에 접근해 영상을 가져와야함.
    return render(request,'health_do/health_do.html',{'video_path':"/static/media/부메랑.mp4"})

from django.http import JsonResponse

def upload_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        
        # video_file을 원하는 방식으로 처리합니다.
        # 예: 파일 저장, 데이터베이스에 저장, 비디오 처리 등

        return JsonResponse({'message': 'Video uploaded successfully.'})
    
    return JsonResponse({'error': 'Invalid request.'}, status=400)

def health_report(request):
    print("[health_report]")
    #
    video_and_dict_pose_cross_correlation()
    re1 = recommend_contentBased(["leg","head"])
    re2 = recommend_collaborative(["leg","head"])
    print(re1,re2)
    return render(request,'health_do/health_report.html',{'recommend':re1})
 