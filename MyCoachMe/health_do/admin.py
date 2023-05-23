from django.contrib import admin

# Register your models here.
from .models import Train_video
from .models import Training_data

admin.site.register(Train_video)
admin.site.register(Training_data)