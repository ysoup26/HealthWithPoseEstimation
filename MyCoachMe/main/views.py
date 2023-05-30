from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import User_data
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import auth
from django.db import models


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
                return render(request, 'main/signin.html', {'error': '이미 사용 중인 아이디입니다.'})

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

            return redirect('login')

    return render(request, 'main/signin.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # user = auth.authenticate(request, username=username, password=password)
        if User_data.objects.filter(user_id=username, pw=password).exists():
            return redirect(reverse('select', args=(username, )))
        else:
            return render(request, 'main/login.html', {'error': 'username or password is incorrect.'})
    else:
        return render(request, 'main/login.html')


def logout(request):
    if request.method == 'POST':
        return redirect('home')
    return render(request, 'main/login.html')

def select(request, user_id):
    return render(request, 'main/exerciese.html', {'user_id': user_id})
