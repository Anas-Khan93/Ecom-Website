from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from datetime import datetime
import os


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
    cat = models.ForeignKey(Category, on_delete=models.PROTECT)
    prod_id = models.AutoField(primary_key=True)
    prod_name = models.CharField(max_length= 250, blank=False, null=False)
    prod_price = models.FloatField(blank=False, null= False)
    prod_quantity = models.IntegerField(blank=False, null= False)
    prod_descr = models.TextField(blank=False, null=False)
    prod_image= models.ImageField(upload_to= 'products/', blank=False, null=False)
    
    class Meta:
        db_table = 'proddetails'
        managed = True

  
#The PRODUCT IMAGES Model
class ProductsImages(models.Model):
    
    img_id = models.AutoField(primary_key=True)
    prod_id = models.ForeignKey(product, on_delete=models.PROTECT)
    prod_img= models.ImageField(upload_to= 'products/', blank= False, null=False)
    #prod_img_date
    
    class Meta:
        db_table = 'prodimg'
        managed = True
        
    def save(self, *args, **kwargs):
        
        # Get the original filename
        
        if self.prod_img:
            
            ext = self.prod_image.name.split('.')[-1]
            
            #Create a new filename using the current datetime
            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            new_filename = f"{slugify(self.prod_name[:20])}--{timestamp}.{ext}"
            
            # Updating the filename with the new name
            self.prod_img.name = os.path.join('products/', new_filename) 
            
        super(product, self).save(*args, **kwargs)
        
        
    
