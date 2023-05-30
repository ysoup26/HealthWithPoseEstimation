from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import User_data
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import auth
from django.db import models
import os


# Create your views here.
def home(request):
    return render(request, 'main/first_page.html')


def send_to_admin(data):
    try:
        admin_user = User_data.objects.create(
            user_id=data['username'],
            pw = data['password'],
            birth_year=data['birth_year'],
            height=data['height'],
            weight=data['weight'],
            lack_health=data['exercise_area']
        )
        admin_user.save()
        print("User data saved to admin database successfully.")
    except Exception as e:
        print(f"Error saving user data to admin database: {str(e)}")


def signup(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            username = request.POST['username']

            # 사용자명(아이디)의 고유성 확인
            if User_data.objects.filter(user_id=username).exists():
                print("이미 사용중인 아이디.")
                return render(request, 'main/signup.html', {'error': '* 이미 사용 중인 아이디입니다.'})

            password = request.POST['password1']
            birth_year = request.POST.get('birth_year', 2000)
            height = request.POST.get('height', 150)
            weight = request.POST.get('weight', 50)
            exercise_area = request.POST.get('exercise_area', 'arm')

            admin_data = {
                'username': username,
                'password': password,
                'birth_year': birth_year,
                'height': height,
                'weight': weight,
                'exercise_area': exercise_area
            }
            send_to_admin(admin_data)

            return redirect('/main/login/')

    return render(request, 'main/signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username,password)
        user = auth.authenticate(request, username=username, password=password)
        if User_data.objects.filter(user_id=username, pw=password).exists():
            #auth.login(request, user)
            return redirect('/main/'+username+'/select/')
        else:
            return render(request, 'main/login.html', {'error': '* username or password is incorrect.'})
    else:
        return render(request, 'main/login.html')


def logout(request):
    if request.method == 'POST':
        return redirect('home')
    return render(request, 'main/login.html')

def select(request, user_id):
    print("id:",user_id)
    return render(request, 'main/exerciese.html', {'user_id': user_id})

def camera_view(request):
    # video_path = './KakaoTalk_20230529_120107363.mp4'  # 실제 영상 경로를 설정해야 합니다.
    # context = {'video_path': video_path}
    print("in?")
    dir_path = os.path.dirname(os.path.realpath(__file__))
    user_video_path = '/main/videos/webcam.mp4' #시연을 위한 임시 영상
    print(user_video_path)
    print(dir_path)
    
    return render(request, 'main/camera_view.html', {'video_path': user_video_path})
