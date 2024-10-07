import json
import stripe
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
#from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
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
import os
from django.utils.decorators import method_decorator

from django.views.decorators.csrf import csrf_exempt

from .serializers import *
from ..models import *



from django.core.files.storage import default_storage
import stripe




# CRUD USER:
class RegisterView(APIView):
    
    permission_classes = [AllowAny]
    
    
    def post(self, request):
        
        try:
            serializer = RegisterSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    
                    "status":"success",
                    'data': serializer.data
                    
                }, status= status.HTTP_200_OK)
            else:
                return Response({
                    
                    'Status':'failed',
                    'Error message': serializer.errors,
                    
                }, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print( f"Exception occurred {e}")
            return Response({
                
                'Status': 'Failed',
                'Error message': 'An exception occurred while processing the request!'
                
            }, status= status.HTTP_500_INTERNAL_SERVER_ERROR)
            
             
                     
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
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


class UserListView(APIView):
    
    #permission_classes= [IsAdminUser, IsAuthenticated]
    #authentication_classes = [JWTAuthentication]
    permission_classes= [AllowAny]

    
    def get(self,request):
        
        user= User.objects.all()
        
        # we need an additional parameter that is many and it will be set to true to let the serializer know we have many objects.
        serializer = UserDetailSerializer(user, many=True)
        
        return Response({
            
            'status':'success',
            'Data': serializer.data 
            
        }, status= status.HTTP_200_OK )      
        

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
                
                serializer = UserDetailSerializer(user)
                
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


class UserUpdateView(APIView):
    
    authentication_classes= [JWTAuthentication]
    permission_classes= [IsAuthenticated]
    
    def put(self, request, pk, format=None):
        
        try:
            user= User.objects.get(pk=pk)
            
            if user== request.user or request.user.is_superuser:
                
                serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            
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
            user = User.objects.get(email=email)
            token_generator = get_token_generator()
            token = token_generator.make_token(user)
            
            rest_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'token': token})
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
            user = get_object_or_404(User, pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            
        if user is not None and default_token_generator.check_token(user, token):
            serializer = PasswordResetConfirmSerializer(data=request.data)
            
            if serializer.is_valid():
                user.set_password(serializer.validated_data['new password'])
                user.save()
                return Response({
                    'Status': 'Success',
                    'message': 'Password has been reset successfully'
                    }, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                
                'error':'Invalid token or user ID'
                
                }, status= status.HTTP_400_BAD_REQUEST)
   



# MISCELANIOUS API CALLS FOR PRACTICE:
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



    


# CRUD CATEGORY
class CategoryCreationView(APIView):
    
    #permission_classes = [JWTAuthentication]
    #permission_classes = [IsAdminUser]
    permission_classes = [AllowAny]
    
    def post(self, request):
        
        serializer = CategoryCreationSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            #cat_name = serializer.validated_data['cat_name']
            #print(cat_name)
            
            return Response({
                
                'status': 'success',
                'data': serializer.data
                                
            }, status = status.HTTP_200_OK)
            
        else:
            return Response({
                
                'status':'failed',
                'error':serializer.errors,
                
            }, status = status.HTTP_400_BAD_REQUEST)


class CategoryListView(APIView):
    
    permission_classes =[AllowAny]
    
    
    def get(self, request):
        
        try:
            cat = Category.objects.all()
            print(cat)
            
            serializer = CategoryCreationSerializer(cat, many=True)
            print (serializer.data)
            return Response({
                    
                'status': 'success',
                'data': serializer.data
                    
            }, status = status.HTTP_200_OK)
                
        except Category.DoesNotExist:
            return Response({
                
                'status': 'failed',
                'error': 'No category exists'                
            }, status= status.HTTP_404_NOT_FOUND)
         
                
class CategorySingleView(APIView):
    
    permission_classes= [AllowAny]
    
    def get(self, request, pk):
        
        try:
            # get the category
            cat = Category.objects.get(pk=pk)
            
            # get all it's subcategories
            subcat = Category.objects.filter(cat_parent_id=pk)
            
            # pass both in the serializer
            serializer = CategoryCreationSerializer(cat)
            subserializer = CategoryCreationSerializer(subcat, many=True)
            
            # create an empty array to insert all subcat
            array= []
            
            
            for subcat_data in subserializer.data:
                id= (int(subcat_data['cat_id']))
                c = Category.objects.filter(cat_parent_id=id)
                if c.exists():
                    serial = CategoryCreationSerializer(c, many=True)
                    array.append(serial.data)
            
            if subcat is None:
                
                return Response ({
                    
                    'Status':'Success',
                    'category': serializer.data
                    
                })
            else:
                return Response({
                    
                    'Status': 'Success',
                    'Category':serializer.data,
                    'Subcategory': subserializer.data,
                    'subsubcat':array                 
                    
                })    
        
        except Category.DoesNotExist:
            return Response({
                
                'status': 'failed',
                'error': f'Category {pk} does not exist'                
                
            }, status= status.HTTP_400_BAD_REQUEST)
            
 
class CategoryUpdateView(APIView):
     
    #permission_classes = [IsAdminUser, IsAuthenticated]
    #authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
     
    def put(self, request, pk):
              
        try:
            cat = Category.objects.get(pk=pk)
            
            serializer = CategoryCreationSerializer(cat, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                
                return Response({
                    
                    'Status': 'success',
                    'Message': f'Category {pk} has been updated',
                    'data': serializer.data
                }, status= status.HTTP_200_OK)
                
            else:
                return Response({
                    
                    'Status': 'failed',
                    'Error message': serializer.errors
                    
                }, status= status.HTTP_400_BAD_REQUEST)
            
            
        except Category.DoesNotExist:
            return Response({
                
                'Status': 'failed',
                'Error message': f'Category {pk} does not exist'
                
            }, status= status.HTTP_404_NOT_FOUND)
            
   
class CategoryDeleteView(APIView):
    
    permission_classes= [AllowAny]
    
    def delete (self, request, pk):
        
        try:
            
            catdel = Category.objects.get(pk=pk)
            
            catdel.delete()
            
            return Response({
                
                'Status': 'Success',
                'Message': f'Category{pk} deleted Successfully'
                            
            }, status= status.HTTP_200_OK)  
        
        except Category.DoesNotExist:
            return Response({
                
                'Status':'Failed',
                'Error message': 'Category does not exist'
                
            }, status= status.HTTP_404_NOT_FOUND)
   
         
                  




# CRUD PRODUCT
class ProdCreationView(APIView):
    
    def post (self, request):
        
        serializer = ProdCreationSerializer(data=request.data)
        print(serializer)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response ({
                
                'Status': 'Success',
                'data': serializer.data
                
            }, status= status.HTTP_200_OK)
            
        else:
            return Response({
                
                'Status': 'Failed',
                'Error message': serializer.errors
                
            }, status = status.HTTP_400_BAD_REQUEST)
            
         
class ProductListView(APIView):
    
    def get(self, request):
        
        try:
        
            prod = Product.objects.all()
        
            serializer = ProdCreationSerializer(prod, many=True)
            
            return Response({
                
                'Status': 'Success',
                'data': serializer.data
                
            }, status= status.HTTP_200_OK)
            
        except Product.DoesNotExist:
            
            return Response({
                
                'Status': 'failed',
                'Error message': 'No products'
                
            }, status= status.HTTP_404_NOT_FOUND)
 
  
class ProductSingleView(APIView):
    
    def get(self, request, pk):
        
        try: 
            prod = Product.objects.get(pk=pk)
            
            serializer = ProdCreationSerializer(prod)
            
            print(serializer.data)
            
            return Response ({
                
                'Status':'Success',
                'data': serializer.data
                
            }, status= status.HTTP_200_OK)
            
        except Product.DoesNotExist:
            return Response({
                
                'Status': 'failed',
                'Error message': ' Product does not exist'
                
            }, status= status.HTTP_404_NOT_FOUND)


class ProductUpdateView(APIView):
    
    def put(self, request, pk):
        
        try:
            
            prod = Product.objects.get(pk=pk)
            
            serializer = ProdCreationSerializer(prod, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                
                return Response({
                    
                    'Status': 'Success',
                    'message': f'product {pk} updated successfully',
                    'data': serializer.data
                    
                }, status= status.HTTP_200_OK)
                
            else:
                return Response({
                    
                    'status': 'failed',
                    'error': serializer.errors
                    
                }, status= status.HTTP_400_BAD_REQUEST)
                
        except Product.DoesNotExist:
            
            return Response({
                
                'Status': 'failed',
                'Error message': f'Product{pk} does not exist'
                
            }, status= status.HTTP_404_NOT_FOUND)
            

class ProductDeleteView(APIView):
    
    # put permissions
    permission_classes= [AllowAny]
    
    def delete(self, request, pk):
        
        try:
            
            prod = Product.objects.get(pk=pk)
            
            if prod.prod_image:
                default_storage.delete(prod.prod_image.name)
                
            prod.delete()
            
            return Response({
                
                'Status': 'Success',
                'Message': f'Product {pk} deleted Successfully'
            }, status= status.HTTP_200_OK)
            
        except Product.DoesNotExist:
            return Response({
                
                'Status': 'failed',
                'Error': 'Product does not exist'
                
            }, status= status.HTTP_404_NOT_FOUND)
        

      

      
       
            
# CRUD PRODUCT Images
class ProdImagesCreationView(APIView):
    
    def post(self, data):
        
        serializer = ProductsImages(data= request.data)
        
        if serializer.is_valid():
            
            serializer.save()
            
            return Response({
                
                'Status': 'success',
                'Data': serializer.data
                
            }, status= status.HTTP_200_OK)
        else:
            return Response({
                
                'Status': 'Failed',
                'Error message': serializer.errors
                
            })


class ProdImagesListView(APIView):
    
    def get(self, request):
        
        try:
            
            img = ProductsImages.objects.all()
            
            serializer= ProdImageSerializer(img, many=True)
            
            return Response({
                
                'Status': 'Success',
                'Data': serializer.data
                
            }, status= status.HTTP_200_OK)
            
        except ProductsImages.DoesNotExist:
            
            return Response({
                
                'Status': 'failed',
                'Error message': "No product images exists"
                
            }, status= status.HTTP_404_NOT_FOUND)


class ProdImagesSingleView(APIView):
    
    def get(self, request, pk):
        
        try:
            img = ProductsImages.objects.get(pk=pk)
            serializer = ProdImageSerializer(img)
            
            return Response({
                
                'Status': 'Success',
                'Data': serializer.data
                
            }, status= status.HTTP_200_OK)
            
        except ProductsImages.DoesNotExist:
            return Response({
                
                'Status': 'Failed',
                'Error message': ' No image found'
                
            }, status= status.HTTP_404_NOT_FOUND)
                                                       

class ProdImagesUpdView(APIView):
    
    def put(self, request, pk):
        
        try:
            
            img = ProductsImages.objects.get(pk=pk)
            
            serializer = ProdImageSerializer(img, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                
                return Response({
                    
                    'Status': 'Success',
                    'Message': f'image with id:{pk} has been updated',
                    'Data': serializer.data
                    
                }, status= status.HTTP_200_OK)
            
        except ProductsImages.DoesNotExist: 
            return Response({
                
                'Status': 'Failed',
                'Error message': f' No image with id:{pk} exists'
                
            }, status= status.HTTP_404_NOT_FOUND)
        
        
class ProdImagesDelView(APIView):
    
    def delete(self, request, pk):
        
        try:
            img = ProductsImages.objects.get(pk=pk)
            
            if img.prod_img:
                default_storage.delete(img.prod_img.name)
                
            img.delete()
            
            return Response({
                
                'Satus': 'Success',
                'Message': f'image id:{pk} successfully deleted'
                
            }, status= status.HTTP_200_OK)
            
        except ProductsImages.DoesNotExist:
            
            return Response({
                
                'Status': 'Failed',
                'Error message': f' No image with id:{pk} exists'
                
            }, status= status.HTTP_404_NOT_FOUND)
            
            
            

# CRUD ORDERS:
# Beginning from this view, all the API methods will be called in one single class. Respecting the DRY principle and following Django's best practice.

class CartView(APIView):
    
    stripe.api_key= settings.STRIPE_KEY
    
    
    
    # CREATE
    def post(self, request):
        
        serializer = CartSerializer(data= request.data)
        print (serializer)
        
        cartuser = serializer.initial_data['user']
        print("cartuser: ",cartuser)

            
        if serializer.is_valid():
            # NEED TO SAVE THE SERIALIZER AFTER DONE WITH TESTING
            #carttotal = serializer.validated_data
            #print("cartotal: ",carttotal)
            
            cart = serializer.save()
            
            print("cart_items: ",cart.items)
            
            # items = cart['items']
            total= 0
            line_items = []
            
            for  item in cart.items.all():
                #product_name = item['product'].prod_name
                product_name = item.product.prod_name
                #product_price = item['product'].prod_price
                product_price = item.product.prod_price
                #quantity = item['quantity']
                quantity = item.quantity
                total += (product_price * quantity)

                line_items.append({
                    
                    'price_data': {
                        
                        'currency': 'usd',
                        'product_data': {
                            
                            'name': product_name,
                        },
                        
                        'unit_amount': int(product_price * 100),
                    },
                    'quantity': quantity, 
                })
                
                # Call stripes payment session
                print("total: ", total)
                
            try:
                checkout_session = stripe.checkout.Session.create(
                        
                    payment_method_types = ['card'],
                    line_items= line_items,
                    mode= 'payment',    
                    # success_url = request.build_absolute_uri( reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
                    # cancel_url = request.build_absolute_uri( reverse('payment_cancelled')),
                    client_reference_id = cart.cart_id, # for cart_id
                    
                metadata= {
                    'cart_id': cart.cart_id,
                    'user_id': cartuser,
                    'total_amount': total,
                    
                    },
                    success_url = request.build_absolute_uri('/') + '?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url = request.build_absolute_uri('/'),                           
                )
                    
                    # Now return the Stripe session id to the frontend
                return Response({
                        
                    'id': checkout_session.id,
                    'stripe_checkout_url': checkout_session.url
                        
                }, status= status.HTTP_200_OK)
                    
                
            except Exception as e:
                return Response({
                        
                    'Status': 'Exception Occured',
                    'Error message': str(e),
                        
                }, status= status.HTTP_400_BAD_REQUEST)
            
                
        else:
            return Response ({
                    
                'Status': 'failed',
                'Error message': serializer.errors
                    
            }, status= status.HTTP_400_BAD_REQUEST)


     
    # READ (the whole cart of all carts as admin)
    def get(self, request, pk=None):
        
        if pk:            
            try:
                cart_obj = Cart.objects.get(pk=pk) 
                serializer = CartSerializer(cart_obj)
                
                return Response({
                        
                    'Status': 'Success',
                    'data': serializer.data
                        
                }, status= status.HTTP_200_OK)
                
            except Cart.DoesNotExist:
                return Response({
                    
                    'Status': 'Failed',
                    'Error message': f'No Cart with id{pk} found'
                    
                }, status= status.HTTP_404_NOT_FOUND)
                
                
        else:
            
            try:
                carts = Cart.objects.all()
                serializer = CartSerializer(carts, many= True)
                
                return Response({
                        
                    'Status': 'Success',
                    'data': serializer.data
                        
                }, status= status.HTTP_200_OK)
            
            except Cart.DoesNotExist:
                return Response({
                    
                    'Status': 'Failed',
                    'Error message': 'No carts exists'
                    
                }, status= status.HTTP_400_BAD_REQUEST)
                


    # UPDATE (Products and their quantity from the cart)
    def put(self, request, pk):
        
        try:
            # Fetch the cart by it's ID
            cart_obj = Cart.objects.get(pk=pk)
            
            # Get the items in the cart
            cart_items_data = request.data.get('items', [])
            
            # List to store updated items for response:
            updated_items = []
            
            for item_data in cart_items_data:
                cart_item_id = item_data.get('cart_item_id')
                
                if not cart_item_id:
                    return Response({
                    
                    'Status': 'Failed',
                    'Error message': 'Cart item ID is required'
                    
                }, status= status.HTTP_400_BAD_REQUEST)
                
                
                
                try:
                    # Fetch each cart item
                    cart_item = CartItems.objects.get(cart= cart, pk= cart_item_id)
                    
                except CartItems.DoesNotExist:
                    return Response({
                        
                        'Status': 'Failed',
                        'Error message': f'No Cart item with id: {cart_item_id} exists'
                        
                    }, status= status.HTTP_404_NOT_FOUND)
                    
                # Update the cart_item using CartItemSerializer:    
                serializer = CartItemSerializer(cart_item, data= item_data , partial=True)
            
                if serializer.is_valid():
                    serializer.save()
                    # Add updated itemms to the list
                    updated_items.append(serializer.data)
            
                else:
                    return Response ({
                    
                        'Status': 'failed',
                        'Error message': serializer.errors
                    
                    }, status= status.HTTP_400_BAD_REQUEST)
                
            return Response({
            
                'Status': 'Success',
                'Message': f'cart successfully updated',
                'updated_items': updated_items
            
            }, status= status.HTTP_200_OK)
                
        except Cart.DoesNotExist:
            return Response({
                
                'Status': 'Failed',
                'Error message': f'No cart with id {pk} found'
                
            }, status= status.HTTP_404_NOT_FOUND)
        
    
    
    # DELETE (Items from the CART)
    def delete(self, request, pk):
        
        try:
            cart= Cart.objects.get(pk=pk)
            
            # Check if a specific cart item is being requested for deletion
            if cart_item_id:
                
                try:
                    # Fetch the individual cart item
                    cart_item = CartItems.objects.get(cart= cart, pk= cart_item_id)
                    
                    # Delete the specific cart item
                    cart_item.delete()
                    
                    return Response({
                        
                        'Status': 'Success',
                        'Message': f'Cart item {cart_item_id} has been deleted'
                        
                    }, status= status.HTTP_200_OK)
                    
                except CartItems.DoesNotExist:
                    return Response({
                        
                        'Status': 'Failed',
                        'Error message': 'Cart item {cart_item_id} does not exist '
                        
                    }, status= status.HTTP_404_NOT_FOUND)  
            
            else:
                # OPTION-1: delete all items in the cart
                cart.items.all().delete()
                
                # OPTION-2: delete the cart itself
                cart.delete()
            
        except Cart.DoesNotExist:
            return Response ({
                
                'Status': 'Failed',
                'Error message': f'No cart with id {pk} found'
                
            }, status= status.HTTP_404_NOT_FOUND)
            



@method_decorator(csrf_exempt, name= 'dispatch')
class StripeWebhookView(APIView):
    
    def post(self, request, *args, **kwargs):
        
        payload =request.body
        print("payload: ",payload)
        
        sig_header = request.META['HTTP_STRIPE_SIGNATURE'] 
        print("sig_header: ", sig_header)
        
        endpoint_secret = settings.STRIPE_WEBHOOK
        print("endpoint_secret: ", endpoint_secret)
        
        
        try:
            event = stripe.Webhook.construct_event(
                
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return HttpResponse("Invalid payload", status= 400)
            
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse("Invalid Signature", status= 400)
            
        
        # Handle the event(if succeeded):
        if event['type'] == 'checkout.session.completed':
            
            session = event['data']['object']
            
            # payment was successful so now we can find the cart and update the quantities in the product
            cart_id = session['metadata'].get('cart_id')
            print("cart_id :", cart_id)
            
            user_id = session['metadata'].get('user_id')
            print("user_id :", user_id)
            
            total_amount = session['metadata'].get('total_amount')
            
            # Fetch the cart and items
            cart_items = CartItems.objects.filter(cart_id= cart_id)
            
            # Remove the item_quantity from the product_quantity
            for item in cart_items:
                product = item.product
                
                #Deduct product quantity:
                if item.quantity >product.prod_quantity:
                    raise ValueError("Not enough stock for this product")
                
                product.prod_quantity -= item.quantity
                product.save()
                
            # Create the order successful payment
            self.create_order(user_id, cart_id, total_amount)
                
                
            return HttpResponse("Payment successful", status= 200)
            
        # Handle the event (if failed):
        elif event['type'] == 'payment_intent.payment_failed':
            
            session = event['data']['object']
            return HttpResponse("Payment failed", status= 200)   
            
        return HttpResponse("Unhandled event type", status= 400)
    
    
    def create_order(self, user_id, cart_id, total_amount):
        
        '''
        CREATE AN ORDER AFTER PAYMENT IS CONFIRMED
        '''

        # Fetch the user based on user_id
        user = get_object_or_404(User, id=user_id)
        
        # Fetching userprofile instance to make cart work:
        userprofile = get_object_or_404(UserProfile, user_id = user_id)
        
        # Fetch cart instance based on cart_id
        cart = get_object_or_404(Cart, pk=cart_id, user = userprofile)
        
        total= total_amount
        
        # EMPTY CART ERROR:
        if not cart.items.exists():
            return {'error':'Cart is empty'}
        
        # get the total amount from the cart
        # total_amount= cart.total_amount
        
        # Now CREATE THE ORDER:
        order = Order.objects.create(
            
            user= cart.user,
            cart=cart,
            customer_email=user.email,
            order_total_amount= total,
            post_code= "M146PN",
            deliv_add= "Mulholand drive",          
            
        )
        
        print("I am order: ", order)
        return order
        
        
        

#  PAYMENT SUCCEEDED AND PAYMENT CANCELLED WILL NOT BE USED ONCE WEBHOOKS ARE EMPLOYED
#class PaymentSuccessView(APIView):
    
    def get(self, request, *args, **kwargs):
        
        session_id = request.GET.get('session_id')
        
        try:
            # Retrieve the session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            # You can verify the payment status here:
            
            if session.payment_status == 'paid':
                return Response({
                    
                    'Status': 'success',
                    'Message': 'payment succeeded',
                    'Session': session.id,
                    
                }, status= status.HTTP_200_OK )
            
            else:
                return Response({
                    
                    'Status': 'failed',
                    'Message': 'payment not confirmed'                   
                    
                }, status= status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                
                'status': 'failed',
                'Error message': 'exception '+ str(e)+ ' has occured'               
                
            }, status= status.HTTP_424_FAILED_DEPENDENCY)
            
            
#class PaymentCancelledView(APIView):
    
    def get(self, request, *args, **kwargs):
        
        return Response({
            
            'Status': 'failed',
            'Message': 'Payment Cancelled, please try again!'
        }, status= status.HTTP_400_BAD_REQUEST)
            



# INCOMPLETE
