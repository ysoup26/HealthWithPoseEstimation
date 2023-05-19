from django.urls import path

from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('health_do/',views.health_do,name='health_do'),
    path('health_report/',views.health_report,name='health_report'),
]