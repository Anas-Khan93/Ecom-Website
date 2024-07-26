from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django_rest_passwordreset.tokens import get_token_generator
from ai_appinterviewer.models import UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    
    first_name = serializers.CharField( required=True, max_length=250)
    last_name = serializers.CharField( required=True, max_length=250)
    email = serializers.EmailField( required=True )
    password = serializers.CharField( write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        
        model=UserProfile
        fields = ('first_name', 'last_name', 'email', 'password')
           
    def validate_email(self,value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists, Please Login instead.")
        return value
            
    def create(self,validated_data):
        user = User(
                              
            username = validated_data['email'],
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],

        )
        user.set_password(validated_data['password'])
        user.save()         
                 
        # create a userprofile instance
        user_profile = UserProfile.objects.create(
            
            user=user,
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            email= validated_data['email'],
            password= user.password  
            )
        
        return user_profile
  
        


class LoginSerializer(serializers.Serializer):
    
    email= serializers.EmailField(required= True)
    password = serializers.CharField( write_only=True, required= True)
        
    def validate(self, data):
        
        #get the email and password
        email = data.get('email')
        password = data.get('password')
        
        #if the dumbass did'nt type the email or password. Tell him to
        if not email:
            raise serializers.ValidationError({"Email": "Email is required"})
        if not password:
            raise serializers.ValidationError({"password": "password is required"})
            
        user = authenticate(username = email, password = password)
            
        if user is None:    
            raise serializers.ValidationError("Invalid Email or Password")
          
        data['user'] = user
        return data
    
    # def resetPassword(self,data):
        
    #     password = data.get('password')
        

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
        