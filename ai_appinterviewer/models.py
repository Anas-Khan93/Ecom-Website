from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

# Create your models here.

# USER MODEL:
class UserProfile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    #defining the model fields here
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    class Meta:
        db_table = 'user_profile'
        managed = True

# THE A.I PLAN MODEL
# class IdPlan(models.Model):
#     plan_id = models.IntegerField(null=False, blank=False)
    
#     class Meta:
#         db_table = 'aiplanscheme'
#         managed= True

# CHATGPT MODEL:
