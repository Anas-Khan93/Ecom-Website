from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    
    first_name = serializers.CharField( required = True, max_length=250 )
    last_name = serializers.CharField( required = True, max_length= 250)
    email = serializers.EmailField(required=True)
    password = serializers.CharField( write_only=True, required=True, validators=[validate_password] )
    
    class Meta:
        
        model=User
        fields = ('first_name', 'last_name', 'email', 'password')
        
    def validate_email(self,value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists, Please Login instead.")
        return value
            
    def create(self,validated_data):
        user = User.objects.create(
                  
            first_name=validated_data['first_name'],
            last_name = validated_data['last_name'],
            email = validated_data['email'],
            username=validated_data['email']
        )
        user.set_password(validated_data['password'])  
        user.save()
        return user 
        


class LoginSerializer(serializers.Serializer):
    
    email= serializers.EmailField(required= True)
    password = serializers.CharField( write_only=True, required= True)
        
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if not email:
            raise serializers.ValidationError({"Email": "Email is required"})
        if not password:
            raise serializers.ValidationError({"password": "password is required"})
            
        user = authenticate(username = email, password = password)
            
        if user is None:
            raise serializers.ValidationError("Invalid Email or Password")
        
        
        data['user'] = user
        return data
        
    