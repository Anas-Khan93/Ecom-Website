from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
#from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.shortcuts import render
import requests
import pprint
from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404
from . import serializers as seria


# CREATE USER:
class RegisterView(APIView):
    
    permission_classes = [AllowAny]
    
    
    def post(self, request):
        
        try:
            serializer = seria.RegisterSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({"status":"success"}, status= status.HTTP_200_OK)
            else:
                return Response({
                    
                    'Status':'failed',
                    'Error message': serializer.errors,
                    
                }, status = status.HTTP_400_BAD_REQUEST)
        except:
            print("Exception occurred")
 
                           
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = seria.LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'status': 'success',
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token)
                }, status=status.HTTP_200_OK)
                
            else:
                # User authentication failed
                return Response({
                    'status': 'failed',
                    'error': 'Invalid username or password'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Serializer validation failed
            return Response({
                'status': 'failed',
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # # This should never be reached, but if it does, return an error response
        # return Response({
        #     'status': 'error',
        #     'message': 'Unexpected error occurred'
        # }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# READ ALL USERS (REQUIRES ADMIN PRIVILIDGES):
class UserListView(APIView):
    
    permission_classes= [IsAdminUser, IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    
    def get(self,request):
        
        user= User.objects.all()
        
        # we need an additional parameter that is many and it will be set to true to let the serializer know we have many objects.
        serializer = seria.UserDetailSerializer(user, many=True)
        
        return Response({
            
            'status':'success',
            'Data': serializer.data 
            
        }, status= status.HTTP_200_OK )      
        

# READ USER (REQUIRES USER/ADMIN TO BE LOGGED IN ):
class UserProfileView(APIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    # In DRF format=None, allows client to specify the desired format of the response data. example a client might request  a response
    # like Json, XML or another format. 
    def get(self, request, pk, format=None):
        
        # first we get the user object from the USER table based on id which is pk here
        try:
            
            user = User.objects.get(pk=pk)
            
            if user == request.user or request.user.is_superuser is True:
                
                serializer = seria.UserDetailSerializer(user)
                
                return Response({
                    
                    'status':'success',
                    'error': serializer.data
                }, status= status.HTTP_200_OK)
                
            else:
                return Response({
                        
                    'status':'failed',
                    'error': 'You are not authorized to access this user'
                        
                }, status= status.HTTP_401_UNAUTHORIZED)
            
        except User.DoesNotExist:
            return Response({
                
                'status': 'failed',
                'error': 'User does not exist'
                }, status= status.HTTP_404_NOT_FOUND)
    

    # def put(self, request, pk, format=None):
        
        
    # def delete(self, request, pk, format=None):


# UPDATE USER (REQUIRES USER/ADMIN TO BE LOGGED IN):
class UserUpdateView(APIView):
    
    authentication_classes= [JWTAuthentication]
    permission_classes= [IsAuthenticated]
    
    def put(self, request, pk, format=None):
        
        try:
            user= User.objects.get(pk=pk)
            
            if user== request.user or request.user.is_superuser:
                
                serializer = seria.UserUpdateSerializer(user, data=request.data, partial=True)
            
                if serializer.is_valid():
                    serializer.save()
                    
                    return Response({
                        
                        'status':'successfully updated',
                        'message' : f'User {pk} has been updated with the following details ',
                        'data': serializer.data
                        
                    }, status= status.HTTP_200_OK)
                    
                else:
                    return Response({
                        
                        'status':'failed',
                        'error': serializer.errors                   
                        
                    }, status= status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            return Response({
                
                'status': 'failed',
                'error': 'User does not exist'
                
            }, status= status.HTTP_404_NOT_FOUND)
            

# DELETE USER (REQUIRES USER TO BE LOGGED IN):
class UserDeleteView(APIView):
    
    permission_classes = [IsAdminUser ,IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def delete(self, request, pk):
        
        try:
            user = User.objects.get(pk=pk)
            
            #check if the user making the request is the same user he is fetching and deleting
            if user == request.user:
                #first we delete the UserProfile instance
                up = user_profile.objects.get(user=user)
                up.delete()
                
                # then we delete the user
                # No need to call the serializer
                user.delete()
                return Response({
                        
                    'status':'Success',
                    'message': f'User {pk} has been deleted successfully'                  
                        
                }, status= status.HTTP_200_OK)
                
            else:
                return Response({
                    
                    'status': 'failed',
                    'error': 'You are not allowed to delete this user'
                    
                }, status= status.HTTP_401_UNAUTHORIZED)
            
        except User.DoesNotExist:
            
            return Response ({
                
                'status': 'failed',
                'error':'user does not exist'
                                
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
   
  

class ProductProfitCalculator(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        
        print(data)
        
        serializer = ProductProfitSerializer(data= request.data)
        
        if serializer.is_valid():
            
            profit = serializer.validated_data['profit']
            profit_margin = serializer.validated_data['profit_margin']
            return Response({
                
                'Status': 'Success',
                'data':{
                    
                    'profit': profit,
                    'profit_margin': profit_margin,
                } 
                
            },status = status.HTTP_200_OK )
        else:
            return Response({
                
                'status': 'failed',
                'Error Message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
            
class EmiCalculatorView(APIView):
    
    permission_classes= [AllowAny]
    
    def post (self, request):
        
        serializer= EMIcalcSerializer(data=request.data)
        if serializer.is_valid():
            
            emi = serializer.validated_data['emi']
            return Response({
                
                'status': 'Success',
                'data': {
                    
                    'emi': emi
                }      
            }, status= status.HTTP_200_OK)
            
        else:
            return Response({
                
                'status':'failed',
                'Error message': serializer.errors
                
            }, status= status.HTTP_400_BAD_REQUEST)    
        

class BookFinder(APIView):
    
    permission_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        
        # define the 3rd part API url
        url = 'https://www.googleapis.com/books/v1/volumes?q='
        
        # get query parameter from the main url
        
        state = request.headers
        #print(state)
        
        book = request.GET.get('book')
        
        # make it into a dictionary
        data={'book':book}

        #serialize the data for validation
        serializer = BookFinderSerializer(data=data)
        
        #validate the data
        if serializer.is_valid():
            
            queparam = serializer.validated_data['book']

            # Join the url with the query parameter to send to the 3rd party api
            google_url= url + queparam

            # make the call to the 3rd party now that you have the url
            response = requests.get(google_url)
            
            pprint.pprint(response.headers)
            
           # state1 = response.headers.get('Content-Type ')
            print("Content-Type of the response is: ",response.headers.get('Content-Type'))
            
            #check the status code of the request to the 3rd party API
            stat= response.status_code
            
            if stat == 200:
                
                data = response.json()
                #data = data['items']
                
                data = data['items']
                #pprint.pprint(data)
                
                #our empty list to store our required data in
                finalList= []

                
                for subkey in data:
                    
                    for subsubkey, trueval in subkey.items():
                            
                        if subsubkey =='selfLink':
                                
                            newDict ={}
                            newDict["selfLink"] = trueval
                            finalList.append(newDict)
                

                return JsonResponse({
                    
                    'status':'success',
                    'Data': finalList
                    
                }, status = status.HTTP_200_OK)


                return Response({
                    
                    'status':'failed',
                    'Error message': serializer.errors
                
            }, status =status.HTTP_400_BAD_REQUEST )


class CategoryView(APIView):
    
    permission_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        
        serializer = CategorySerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            cat_name = serializer.validated_data['cat_name']
            print(cat_name)
            
            return Response({
                
                'status': 'success',
                'message': 'Category ' + cat_name + ' successfully created',
                                
            }, status = status.HTTP_200_OK)
            
        else:
            return Response({
                
                'status':'failed',
                'error':serializer.errors,
                
            }, status = status.HTTP_400_BAD_REQUEST)
        