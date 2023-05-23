from django.db import models
from main.models import User_data

class Train_video(models.Model):
    video_name = models.CharField(max_length=20)
    video_id = models.IntegerField(primary_key=True)
    main_body = models.CharField(max_length=20)

    def __str__(self):
        return str(self.video_id)+self.video_name

class Training_data(models.Model):
    user_id = models.ForeignKey(User_data, on_delete=models.CASCADE)
    video_id = models.ForeignKey(Train_video, on_delete=models.CASCADE)
    Rarm = models.FloatField()
    Larm = models.FloatField()
    Relbow = models.FloatField()
    Lelbow = models.FloatField()
    Rwaist = models.FloatField()
    Lwaist = models.FloatField()
    Rleg = models.FloatField()
    Lleg = models.FloatField()
    Rknee = models.FloatField()
    Lknee = models.FloatField()

    def __str__(self):
        return self.user_id.user_id