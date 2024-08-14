from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

# Create your models here.

# THE USER MODEL:
class UserProfile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    #defining the model fields here

    username = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    email = models.EmailField(unique=True)  
    password = models.CharField(max_length=128)
    user_created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_profile'
        managed = True
        

# THE Category Model
class Category(models.Model):
        
        #define the fields here
    cat_id= models.AutoField(primary_key=True)
    cat_parent_id= models.IntegerField ()
    cat_name = models.CharField(max_length=250)
        
    class Meta:
        db_table = 'category'
        managed = True
        
        
# The PRODUCT Model:
class product(models.Model):
    
    #define the fields here
    cat_id = models.ForeignKey(CategoryList, on_delete=models.PROTECT)
    prod_id = models.AutoField(primary_key=True)
    prod_name = models.CharField(max_length= 250, blank=False, null=False)
    prod_price = models.FloatField(blank=False, null= False)
    #prod_image = models.ImageField(required=True, )
    prod_quantity = models.IntegerField(blank=False, null= False)
    prod_descr = models.TextField(required=True)
    
    class Meta:
        db_table = 'proddetails'
        managed = True
    
    
    
