from django.urls import path

from . import views

#나중에는 ''부분에 'health_do/'가 놓여지게 될 것으로 예상
urlpatterns = [
    path('',views.index,name='index'),
    path('health_do/',views.health_do,name='health_do'),
    path('health_report/',views.health_report,name='health_report'),
    path('upload/', views.upload_video, name='upload_video'),
]