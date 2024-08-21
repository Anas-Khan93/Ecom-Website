from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django_rest_passwordreset.tokens import get_token_generator
from ai_appinterviewer.models import Category, UserProfile, product, ProductsImages
import logging
from django.core.files.storage import default_storage

# CREATE USER
class RegisterSerializer(serializers.Serializer):
    
    # username = serializers.CharField(required=True, max_length=250)
    # first_name = serializers.CharField( required=True, max_length=250)
    # last_name = serializers.CharField( required=True, max_length=250)
    # email = serializers.EmailField( required=True )
    # password = serializers.CharField( write_only=True, required=True, validators=[validate_password])

    
    class Meta:
        
        model=UserProfile
        fields = '__all__'
        read_only_fields = ['user', 'user_created_at']
           
    def validate_email(self,value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists, Please Login instead.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value    
            
    def create(self,validated_data):
        user = User(
                              
            username = validated_data['username'],
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name']

        )
        user.set_password(validated_data['password'])
        user.save()         
                 
        # create a userprofile instance
        user_profile = UserProfile.objects.create(
            
            username=validated_data['username'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            email= validated_data['email'],
            password= user.password  
            )
        
        return user_profile
  

class LoginSerializer(serializers.Serializer):
    
    username= serializers.CharField(required= True, max_length=250)
    password = serializers.CharField( write_only=True, required= True)
        
    def validate(self, data):
        
        #get the email and password
        username = data.get('username')
        password = data.get('password')
        
        #if the dumbass did'nt type the email or password. Tell him to
        if not username:
            raise serializers.ValidationError({"Username": "Username is required"})
        if not password:
            raise serializers.ValidationError({"password": "password is required"})
        
        # remember the authenticate function by default uses USERNAME and PASSWORD to authenticate the user.  
        user = authenticate(username = username, password = password)
            
        if user is None:    
            raise serializers.ValidationError("Invalid username or Password")
          
        data['user'] = user
        return data

# READ USER
class UserDetailSerializer(serializers.Serializer):
    
    username = serializers.CharField(required=True, max_length=250)
    first_name = serializers.CharField( required=True, max_length=250)
    last_name = serializers.CharField( required=True, max_length=250)
    email = serializers.EmailField( required=True )

    def validate(self, data):
        
        return data
    
    def create(self, validated_data):
        
        username = validated_data['username']
        

# UPDATE USER       
class UserUpdateSerializer(serializers.Serializer):
    
    username = serializers.CharField(required=True, max_length= 250)
    email = serializers.EmailField(required=True)
    
    class Meta:
        model= User
        fields = ('username', 'email')
    
    def validate_email(self, value):
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(email=value).exclude(pk=user_id).exists():
            raise serializers.ValidationError("Email already exists!")
        return value
    
    # validate the username as in whether the new username is not
    def validate_username(self, value):
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(username=value).exclude(pk=user_id).exists():
            raise serializers.ValidationError("Username already exists.")
        return value
    
    # include the following parameters as you are updating the instance with the validated data
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        
        # now we update the userprofile model
        # there is another method which involves creating a signal that creates user_profile instance instead of having it saved here!
        print(instance)
        user_profile = UserProfile(user=instance)
        user_profile.username = instance.username
        user_profile.email = instance.email
        user_profile.save()
        
        return instance


# Validating the user before he sending the reset link
class PasswordResetSerializer(serializers.Serializer):

    email = serializers.EmailField(required = True)
    
    def validate_email(self,value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user associated with this email found !")
        return value


# Creating a token to send to the user when he clicks the link
class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only= True, validators=[validate_password])
    
    def validate(self,data):
        token = data.get('token')
        password = data.get('password')
        
        token_generator = get_token_generator()
        user = token_generator.get_user_for_token(token)
        
        if not user or not token_generator.check_token(user, token):
            raise serializers.ValidationError("Invalid or expired token! ")
        
        data['user'] = user
        return data
    
    def save(self):
        user = self.validated_data['user']
        password = self.validated_data['password']
        
        user.set_password(password)
        user.save()
        
        
class ProductProfitSerializer(serializers.Serializer):
    
    revenue = serializers.IntegerField(required=True)
    cost = serializers.IntegerField(required=True)
    total_products_sold = serializers.IntegerField(required= True)
    
    def calculate(self, data, revenue, cost):
        # profit = revenue - cost
        profit = data['revenue'] - data['cost']
        print(profit)
        
        # profit_margin = (profit / revenue)*100
        profit_margin = (profit / data['revenue']) * 100
        print(profit_margin)
        
        data['profit']= profit
        data['profit_margin'] = profit_margin
        return data
    
    
    def validate(self, data):
        
        revenue = data.get('revenue')
        cost = data.get('cost')
        total_products_sold = data.get('total_products_sold')
        
        # data = self.calculate(data, revenue, cost)
        data = self.calculate(data)
        
        print(data)
        return data
        

class EMIcalcSerializer(serializers.Serializer):
    
    p= serializers.FloatField(required= True)
    r= serializers.FloatField(required= True)
    n= serializers.IntegerField(required= True)
    
    # VALIDATE PARAMETERS Function
    def validate(self, data):
        
        p= data.get('p')
        r= data.get('r')
        n= data.get('n')
        
        if data['n'] < 18 or data['n'] > 60:
            raise serializers.ValidationError("The number of months 'r' should be between 16 to 60 months.")
        else:
            data= self.findemi(data)
        
        print(data)
        return data
    
    # CALCULATE EMI Function
    def findemi(self, data):
              
        data['r']= (data['r'] / 100) / 12
          
        emi= data['p'] * data['r'] * ((1 + data['r'])**data['n']) / (( 1 + data['r'])**data['n'] - 1)
        
        data['emi'] = emi
        return data


class BookFinderSerializer(serializers.Serializer):
    book = serializers.CharField( required=True )
    
    def validate(self,data):
        book = data.get('book')
        
        if not book:
            raise serializers.ValidationError({"Error":"a book category is required"})
        
        return data
    

class CategoryCreationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields= '__all__'
        read_only_fields = ["cat_id"]

    # Meta class is generally used for Model Serializer REMEMBER SIMBA

    
    def validate(self, data):
        
        cat_parent_id = data.get('cat_parent_id')
        cat_name = data.get('cat_name')
        
        if not cat_name:
            raise serializers.ValidationError("Please enter a category name")
        
        # Fetch all objects of each parent id and check if the category already exists either main or sub...
        if Category.objects.filter( cat_parent_id=cat_parent_id ,cat_name=cat_name).exists():
            raise serializers.ValidationError("Category already present. Cannot create duplicate categories!")
        
        
        return data
    
    # Once the data is validated it will be either passed back to the view or used to create new objects or update them
    def create (self, validated_data):
        
        cat = Category.objects.create(
            
            cat_parent_id = validated_data['cat_parent_id'],
            cat_name= validated_data['cat_name']
        )
        
        print(cat)
        
        return cat
    
    def update(self, instance, validated_data):
        
        instance.cat_parent_id = validated_data.get('cat_parent_id', instance.cat_parent_id)
        instance.cat_name = validated_data.get('cat_name', instance.cat_name)
        instance.save()
        
        
        #print(cat_name)
        return instance
    

                                    #NEW METHOD
# ************************************************************************************
#CRUD PRODUCT (using model serializer)
# ModelSerializer fully maps all the fields that we want defined in our model. It helps in not having to define each value again in 
# the serializer. 


class ProdCreationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = product
        fields = '__all__'
        read_only_fields= ["prod_id"]
        
        
    def validate(self,data):
        
        cat = data.get('cat')
        prod_name = data.get('prod_name')
        
        # CHECK IF A CATEGORY WITH ID USER GAVE EXISTS
        if not Category.objects.filter(cat=cat).exists():
            raise serializer.ValidationError(f"Category with id:{cat} doesnot exist")
        
        # CHECK IF A PRODUCT WITH SAME NAME ALREADY EXISTS
        if product.objects.filter(cat=cat, prod_name=prod_name).exists():
            raise serializers.ValidationError("Product already exists in that category!")
        
        # return the validated data back to the view
        return data
    
        
    def create(self, validated_data):
        
        prod = product.objects.create(
            
            cat= validated_data['cat'],
            prod_name= validated_data['prod_name'],
            prod_price= validated_data['prod_price'],
            prod_quantity= validated_data['prod_quantity'],
            prod_descr= validated_data['prod_descr']
            
        )
        
        return prod
    
    def update(self, instance, validated_data):
        
        # Update the instance with new data
        instance.cat = validated_data.get('cat', instance.cat)
        instance.prod_name = validated_data.get('prod_name', instance.prod_name)
        instance.prod_price = validated_data.get('prod_price', instance.prod_price)
        instance.prod_quantity = validated_data.get('prod_quantity', instance.prod_quantity)
        instance.prod_descr = validated_data.get('prod_descr', instance.prod_descr)

        # save the updated value before returning it to the view   
        instance.save()
        return instance
            

    
class ProdImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductsImages
        fields = ("img_id", "prod_id", "prod_img_url" )
        read_only_fields = ["img_id"]
    
     
    def validate(self, data):
        
        prod_id = data.get('prod_id')
        
        # CHECK IF THE PRODUCT_ID USER PROVIDED EXISTS IN PRODUCTS if not then RAISE ERROR
        if not product.objects.filter(prod_id= prod_id).exists:
            raise serializers.ValidationError("Produc with product-id:{prod_id} does not exist.")
        
        return data
        
    
    def create(self, validated_data):
        
        prodimg = ProductsImages.objects.create(
            
            prod_id= validated_data['prod_id'],
            prod_img= validated_data['prod_img'],
            
        )
        
        return prodimg
    
    
    def update(self, instance, validated_data): 
        
        # DELETE PREVIOUS IMAGE FILE UPLOADED TO BLOB STORAGE BEFORE UPLOADING NEW IMAGE
        if 'prod_img' in validated_data:
            if instance.prod_img:
                default_storage.delete(instance.prod_img.name)
        
        # UPDATE INSTANCE WITH NEW DATA
        instance.prod_id = validated_data.get('prod_id', instance.prod_id)
        instance.prod_img = validated_data.get('prod_img', instance.prod_img)
        
        # SAVE THE UPDATED INSTANCE
        instance.save()
        
        return instance