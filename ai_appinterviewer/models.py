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
    user_created_at = models.DateTimeField(auto_now_add=True, null= False, blank= False)

    class Meta:
        db_table = 'user_profile'
        managed = True

        



# CATEGORY MODEL:
class Category(models.Model):
        
        #define the fields here
    cat_id= models.AutoField(primary_key=True)
    cat_parent_id= models.IntegerField (null= False,  blank= False)
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
class Product(models.Model):
    
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
    def delete(self, *args, **kwargs):
        
        self.is_deleted = True
        self.save()








# PRODUCT IMAGES MODEL: (to store product images)
class ProductsImages(models.Model):
    
    img_id = models.AutoField(primary_key=True)
    prod_id = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='prod_id')
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







    # CART MODEL:
    
class Cart(models.Model):
        
    cart_id = models.AutoField(primary_key= True, db_column= 'cart_id')
    user = models.ForeignKey(UserProfile, on_delete= models.CASCADE, db_column='user_id')
    created_at = models.DateTimeField(auto_now_add= True)
        
    class Meta:
        db_table = 'cart'    
        managed = True
    
        
class CartItems(models.Model):
        
    cart_item_id = models.AutoField(primary_key= True, db_column= 'cart_item_id')
    cart = models.ForeignKey(Cart, related_name= 'items', on_delete=models.CASCADE, db_column= 'cart_id' )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column= 'prod_id')   
    quantity = models.PositiveIntegerField(default= 1)
        
    class Meta:
        db_table = 'cart_items'
        managed = True
    
        
    # BUSINESS LOGIC:-    
        
    # Calculating the total price    
    def get_total_price (self):
        
        return self.quantity * self.product.prod_price
        
             
    # Override the save method to adjust the product quantity
    def save(self, *args, **kwargs):
        
        if self.product.is_deleted:
            raise ValueError("Cannot add deleted product to the cart")
            
        # if self.pk is None:
                
        #     #Ensure the product has enough quantity:
        #     if self.quantity > self.product.prod_quantity:
        #         raise ValueError ("Not enough stock for this Product")
                
        #     self.product.prod_quantity -= self.quantity
        #     self.product.save()
                
        super().save(*args, **kwargs)





# CRUD ORDER :  
class Order(models.Model):
    
    # GENERAL KEYS:-
    order_id = models.AutoField(primary_key= True, db_column='order_id')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column= 'user_id')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, db_column= 'cart_id')
    customer_email = models.EmailField(null= False, blank= False)
    
    # ORDER variables:-
    order_placed_at = models.DateField(auto_now_add= True, null= False, blank= False, db_column='order_created_at')
    order_total_amount = models.FloatField(db_column= 'total_amount', blank= True, null= True)

    # choices must be tuples
    order_stat_list = [
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('confirmed', 'Confirmed'),
        ('on the way', 'On the way'),
        ('delivered', 'Delivered'),
        ]
    order_stat = models.CharField(max_length= 50, choices= order_stat_list, default= 'pending')
    

    # REQUIRED VARIABLES:
    post_code = models.CharField(max_length= 500)
    deliv_add= models.TextField()
    
    # MISCELANIOUS OPTIONAL VARIABLE:
    is_gift = models.BooleanField(default= False)   
    
    # SOFT DELETE:
    objects = ProductManager()
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'order'
        managed = True
    

        
    def delete(self, *args, **kwargs):
        
        self.is_deleted = True
        self.save()
            
            
                