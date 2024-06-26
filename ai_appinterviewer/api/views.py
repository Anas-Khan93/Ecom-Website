from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer, LoginSerializer


class RegisterView(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
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