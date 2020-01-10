from django.db import models

# Create your models here.


class Users(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=20,db_index=True)
    password = models.CharField(max_length=20)

    class Meta:
        db_table = 'users'


class Dirs(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=20,db_index=True)
    dir = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'dirs'
