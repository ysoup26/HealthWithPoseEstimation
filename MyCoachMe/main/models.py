
from django.db import models

class User_data(models.Model):
    lack_health_choices = [
        ('arm', '팔꿈치 위 팔'),
        ('elbow', '팔꿈치 아래 팔'),
        ('waist', '허리'),
        ('leg', '허벅지'),
        ('knee', '종아리'),
    ]

    user_id = models.CharField(max_length=20, primary_key=True)
    pw = models.CharField(max_length=20)
    birth_year = models.IntegerField()
    height = models.FloatField()
    weight = models.FloatField()
    lack_health = models.CharField(max_length=10, choices=lack_health_choices)

    def __str__(self):
        return self.user_id


class Models (models.Model):
    user_id = models.ForeignKey(User_data, on_delete=models.CASCADE)
    model_id = models.CharField(max_length=30)

    def __str__(self):
        return self.model_id