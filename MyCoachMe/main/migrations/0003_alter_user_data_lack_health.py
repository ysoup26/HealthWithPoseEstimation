# Generated by Django 3.2.19 on 2023-05-21 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_user_data_lack_health'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_data',
            name='lack_health',
            field=models.CharField(choices=[('arm', '팔꿈치 위 팔'), ('elbow', '팔꿈치 아래 팔'), ('waist', '허리'), ('leg', '허벅지'), ('knee', '종아리')], max_length=10),
        ),
    ]
