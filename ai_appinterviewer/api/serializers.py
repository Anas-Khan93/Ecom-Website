from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django_rest_passwordreset.tokens import get_token_generator
from ai_appinterviewer.models import Category, UserProfile

# CREATE USER
class RegisterSerializer(serializers.Serializer):
    
    username = serializers.CharField(required=True, max_length=250)
    first_name = serializers.CharField( required=True, max_length=250)
    last_name = serializers.CharField( required=True, max_length=250)
    email = serializers.EmailField( required=True )
    password = serializers.CharField( write_only=True, required=True, validators=[validate_password])

    
    class Meta:
        
        model=UserProfile
        fields = ('username','first_name', 'last_name', 'email', 'password')
           
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
            #is_superuser = validated_data['is_superuser']

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
    

class CategoryCreationSerializer(serializers.Serializer):
    
    #these are class variables and they are used to store data when i create an instance of the class
    #I can assign values to them, which can then be accessed and modified using methods within my class
    cat_id = serializers.IntegerField(read_only=True) # if you don't want to ask this as input make it read only
    cat_parent_id = serializers.IntegerField()
    cat_name = serializers.CharField(max_length=250, required=True)
    
    class Meta:
        model = Category
        fields = '__all__'
    
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
    
    

    
