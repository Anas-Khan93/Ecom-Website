from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from datetime import datetime
import os


# Create your models here.



# USER MODEL:
class UserProfile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    #defining the model fields here

    username = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    email = models.EmailField(unique=True)  
    password = models.CharField(max_length=128)
    user_created_at = models.DateTimeField(auto_now_add=True, null= False, blank= False)

    class Meta:
        db_table = 'user_profile'
        managed = True

        



# CATEGORY MODEL:
class Category(models.Model):
        
        #define the fields here
    cat_id= models.AutoField(primary_key=True)
    cat_parent_id= models.IntegerField ()
    cat_name = models.CharField(max_length=250)
        
    class Meta:
        db_table = 'category'
        managed = True
        




# OVERRIDING THE PRODUCT MANAGER:
## To ensure soft_deleted objects are not returned in query

class ProductManager(models.Manager):
    
    def get_queryset(self):
        
        # here what we want to is basically return only the data that has not been soft deleted
        return super().get_queryset().filter(is_deleted= False)


 
# PRODUCT MODEL:
class product(models.Model):
    
    # define the fields here:
    cat = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='cat_id')
    prod_id = models.AutoField(primary_key=True)
    prod_name = models.CharField(max_length= 250, blank=False, null=False)
    prod_price = models.FloatField(blank=False, null= False)
    prod_quantity = models.IntegerField(blank=False, null= False)
    prod_descr = models.TextField(blank=False, null=False)

    # Use the Custom manager
    objects = ProductManager()
    is_deleted = models.BooleanField(default= False)
    
    class Meta:
        db_table = 'proddetails'
        managed = True
    
    # method for soft delete:
    class delete(self, *args, **kwargs):
        
        self.is_deleted = True
        self.save()





# PRODUCT IMAGES MODEL: (to store product images)
class ProductsImages(models.Model):
    
    img_id = models.AutoField(primary_key=True)
    prod_id = models.ForeignKey(product, on_delete=models.CASCADE, db_column='prod_id')
    prod_img= models.ImageField(upload_to= 'products/', blank= False, null=False)
    prod_img_date= models.DateTimeField(auto_now_add=True, null=False, blank=False)
    
    class Meta:
        db_table = 'prodimg'
        managed = True
        
    def save(self, *args, **kwargs):
        
        # Get the original filename
        if self.prod_img:
            
            # split the filename from its extension
            ext = self.prod_img.name.split('.')[-1]
            
            #Create a new filename using the current datetime
            timestamp = datetime.now().microsecond
            new_filename = f"'ecom'{timestamp}.{ext}"
            
            # Updating the filename with the new name
            self.prod_img.name = os.path.join('products/', new_filename) 
            
        super(ProductsImages, self).save(*args, **kwargs)






# CRUD ORDER STATUS:
class OrderStatus(models.Model):
    
    ord_stat_id = models.AutoField(primary_key= True)
    ord_status = models.CharField(max_length= 500, blank= False, null= False, db_column= 'order_status')
    ord_track_no = models.FloatField(db_column= 'order_tracking_no')
     
    class Meta:
        db_table = 'order_status'
        managed= True






# CRUD PAYMENT METHOD:
class PaymentMethod(models.Model):
    
    paym_id = models.AutoField(primary_key= True)
    paymethod = models.CharField(max_length= 500, blank=false, null= False, db_column= 'payment_method')
    
    class Meta:
        db_table = 'payment_method'
        managed = True





class PaymentStatus(models.Model):
    
    paystat_id = models.AutoField(primary_key= True)
    paystat = models.CharField(max_length= 250, blank= False, null= False, db_column='payment_status')

    class Meta:
        db_table = 'payment_status'
        managed = True




      
class ShippingMethod(models.Model):
    
    ship_method_id = models.AutoField(primary_key= True)
    shipmnt_method = models.CharField(max_length= 500, blank= False, null= True, db_column='shipment_method')   
    shipmnt_cost = models.FloatField(blank= False, null= False, db_column= 'shipment_cost')
    
    class Meta:
        db_table = 'shipping_method'
        managed = True





class ShippingStatus (models.Model):
    
    ship_status_id = models.AutoField(primary_key= True)
    shipmnt_status = models.CharField(max_length= 500, blank= False, null= False, db_column= 'shipment_status')
    
    class Meta:
        db_table = 'shipping_status'





# CRUD ORDER :  
class Order(models.Model):
    
    # GENERAL KEYS
    order_id = models.AutoField(primary_key= True, db_column='order_id')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column= 'user_id')
    prod = models.ForeignKey(product, on_delete=models.CASCADE, db_column= 'prod_id')
    customer_email = models.EmailField(null= False, blank= False)
    
    # ORDER variables:
    order_placed_at = models.DateField(auto_now_add= True, null= False, blank= False, db_column='order_created_at')
    order_total_amount = models.FloatField(db_column= 'total_amount')
    order_stat = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, db_column= 'order_status' )
    order_notes = models.TextField(blank= True, null= True)
    order_stat = models.ForeignKey (OrderStatus, on_delete=models.CASCADE, db_column= 'order_status_id')
    
    # PAYMENT KEYS:
    paym_id = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, db_column= 'payment_method_id')
    paystat = models.ForeignKey(PaymentStatus, on_delete=models.CASCADE, db_column= 'payment_status_id')
    
    # SHIPMENT KEYS:
    ship_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE, db_column= 'shipping_method_id')
    ship_status = models.ForeignKey(ShippingStatus, on_delete= models.CASCADE, db_column= 'shipment_status_id')
    
    # REQUIRED VARIABLES:
    post_code = models.CharField(max_length= 500,  )
    deliv_add= models.TextField()
    
    # MISCELANIOUS OPTIONAL VARIABLE:
    deliv_instructions = models.TextField(blank = True, null = True)
    is_gift = models.BooleanField(default= False)
    
    class Meta:
        db_table = 'order'
        managed = True
        
        
        
