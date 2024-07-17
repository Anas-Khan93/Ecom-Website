from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404
from .serializers import RegisterSerializer, LoginSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer


class RegisterView(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"success"}, status= status.HTTP_201_CREATED)
        else:
            return Response({
                
                'Status':'failed',
                'Error message': serializer.errors,
                
            }, status = status.HTTP_400_BAD_REQUEST)
            
                
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        serializer = LoginSerializer(data= request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                
                'Status': 'Success',
                'data': {
                    
                    'authtoken': token.key,
                    'firstName': user.first_name,
                    'lastName': user.last_name,
                    'email': user.email
                }
                
            }, status=status.HTTP_200_OK)
        
        else:
            return Response({
                
                'Status': 'Failed',
                'ErrorMessage': serializer.errors
            }, status= status.HTTP_400_BAD_REQUEST)
            
class PasswordResetView(APIView):
    
    permission_classes=[AllowAny]
    
    def post(self,request):
        serializer = PasswordResetSerializer(data= request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = user.objects.get(email=email)
            token_generator = get_token_generator()
            token = token_generator.make_token(token)
            
            rest_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'token',token})
            )
            
            send_mail(
                'password reset request',
                f'click link to reset your password:{rest_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
                
            )
            return Response({"message": "Password reset link sent !"}, status = status.HTTP_200_OK)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
    
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, uidb64, token, *args, **kwargs):
        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=id)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            
        if user is not None and default_token_generator.check_token(user, token):
            serializer = SetNewPasswordSerializer(data=request.data)
            
            if serializer.is_valid():
                user.set_password(serializer.validated_data['new password'])
                user.save()
                return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error':'Invalid token or user ID'}, status= status.HTTP_400_BAD_REQUEST)
        


            
            
