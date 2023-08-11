from django.db import models
from django.contrib.auth.models import User
import uuid

class Type_gun(models.Model):
    name = models.CharField(max_length=255)
    id = models.AutoField(primary_key=True, editable=False)

    def __str__(self):
        return self.name
    
class ProfileSteam(models.Model):
    id64 = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
class Skin(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    assetid = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return self.name
