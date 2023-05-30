from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('', views.home, name="home"),
                  path('signup/', views.signup, name="signup"),
                  path('login/', views.login, name="login"),
                  path('logout/', views.logout, name='logout'),
                  path('<str:user_id>/select/', views.select, name='select'),
                  path('signup/camera_view', views.camera_view, name='camera_view'),
                  # path('login/',views.login, name="login"),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)