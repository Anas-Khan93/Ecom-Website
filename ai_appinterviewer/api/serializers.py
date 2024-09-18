from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django_rest_passwordreset.tokens import get_token_generator
from ..models import *
import logging
from django.core.files.storage import default_storage


# CREATE USER
class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        
        model= User
        
        #fields that will be returned
        fields = ('user_id','username', 'first_name', 'last_name', 'email', 'password')
        read_only_fields = ["user_id"]
        
           
    def validate_email(self,value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists, Please Login instead.")
        return value

        
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value    
        
            
    def create(self,validated_data):
        
        # Create User instance
        user = User(
                              
            username = validated_data['username'],
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name']

        )
        user.set_password(validated_data['password'])
        user.save()         
                 
        # create a userprofile instance
        user_profile = UserProfile.objects.create( user= user)
        
        return user



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
        


# MISC SERIALIZERS FOR DIFFERENT API CALLS AND OPERATIONS 
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
    


# CRUD CATEGORY
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
# FROM THIS POINT ONWARDS, serializer.serializers shall be replaced by serializer.ModelSerializer fully maps all the fields that we want defined in our model.
# This allows us to keep away from DRY and follow Djangos best practice. 

class ProdCreationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields= ["prod_id"]
        
        
    def validate(self,data):
        
        cat = data.get('cat')
        prod_name = data.get('prod_name')
        
        # CHECK IF A CATEGORY WITH ID USER GAVE EXISTS
        if not Category.objects.filter(cat_id=cat.cat_id).exists():
            raise serializer.ValidationError(f"Category with id:{cat} doesnot exist")
        
        # CHECK IF A PRODUCT WITH SAME NAME ALREADY EXISTS
        if Product.objects.filter(cat=cat, prod_name=prod_name).exists():
            raise serializers.ValidationError("Product already exists in that category!")
        
        # return the validated data back to the view

        return data
    
        
    def create(self, validated_data):

        prod = Product.objects.create(
            
            cat= validated_data['cat'],
            prod_name= validated_data['prod_name'],
            prod_price= validated_data['prod_price'],
            prod_quantity= validated_data['prod_quantity'],
            prod_descr= validated_data['prod_descr']
            
        )
        
        print("prod= ",prod)
        
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
            
            


#CRUD PRODUCT IMAGES SERIALIZER   
class ProdImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductsImages
        fields = ("img_id", "prod", "prod_img_url" )
        read_only_fields = ["img_id"]
    
     
    def validate(self, data):
        
        prod_id = data.get('prod')
        
        # CHECK IF THE PRODUCT_ID USER PROVIDED EXISTS IN PRODUCTS if not then RAISE ERROR
        if not Product.objects.filter(prod_id= prod).exists:
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
    
    



# CartItemsSerializer will process all the items put into the cart made by the user and the Cart will do the rest
class CartItemSerializer(serializers.ModelSerializer):
    
    product_name = serializers.CharField(source= 'product.prod_name', read_only= True)
    product_price = serializers.FloatField(source= 'product.prod_price', read_only= True)
    total_price = serializers.SerializerMethodField()
    cart = serializers.PrimaryKeyRelatedField(read_only= True)
    
    class Meta:
        model=CartItems
        fields = ['cart_item_id', 'cart' ,'product', 'product_name', 'product_price', 'quantity', 'total_price']
        read_only_fields = ['cart_item_id', 'cart']
    
    
        
    def get_total_price(self, obj):
        
        # handling case when 'obj' is a model instance (during serialization)
        
        if isinstance(obj, CartItems):
            product_price = obj.product.prod_price
            quantity = obj.quantity
            
        # Handling case when 'obj' is a dictionary (during deserialization)
        else:
            product_price= obj['product'].prod_price
            quantity= obj['quantity']

        return product_price * quantity
    
    
    # IMPORTANT INFO: DRF looks for methods validate_fieldname for each field in the serializer. So DRF will pass the quantity as value to the method.
    def validate_quantity(self, value):
        
        if value < 1:
            raise serializers.ValidationError("Quantity must be atleast 1")
        
        if self.instance and value > self.instance.product.prod_quantity:
            raise serializers.ValidationError("Not enough stock available")
        
        return value
    
    
    def update(self, instance, validated_data):
        
        new_product = validated_data.get('product', instance.product)
        new_quantity = validated_data.get('quantity', instance.quantity)
        
        if new_quantity > new_product.prod_quantity:
            raise serializers.ValidationError("Not enough Stock !")
        
        if new_quantity == 0:
            instance.delete()
            
        else:
            instance.product = new_product
            instance.quantity = new_quantity
            
            #Save it after storing it
            instance.save()
            
        return instance        
            
                    
        

  
# Cart Serializer will process all the items put into the cart made by the user and the Cart
class CartSerializer(serializers.ModelSerializer):
    
    items = CartItemSerializer(many=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['cart_id', 'user', 'created_at', 'items', 'total_amount']
        read_only_fields = ['cart_id']

    # Calculate the total price for all the items
    def get_total_amount(self, obj):  # Fix the method name to match your field name
         
        
        items = obj['items']  # Use obj.items.all() to get all cart items
        
        for item in items:
            print("I am product: ",item['product'].prod_price)
            print("I am quantity: ", item['quantity'])
            
        total = sum([item['product'].prod_price * item['quantity'] for item in items])
        print("Total: ", total)
        return total  

    def validate(self, data):
        if not data.get('items'):
            raise serializers.ValidationError("Cart is empty!")
        return data

    def create(self, validated_data):
        # Extract the items from the validated_data
        items_data = validated_data.pop('items')
        
        # print Debugging statements
        print(f"Validated Data: {validated_data}")
        print(f"Items Data: {items_data}")
        
        # Create the Cart
        cart = Cart.objects.create(**validated_data)
        
        # More Debugging
        print(f"Created Cart: {cart}")

        # Create the CartItems and associate them with the Cart
        for item_data in items_data:
            print(f"Item Data before CartItem creation: {item_data}")
            CartItems.objects.create(cart=cart, **item_data)  # Explicitly set the cart here

        return cart

       

# ****************INCOMPLETE**********************    
class OrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Cart
        fields = '__all__'
        read_only_fields = ['order_id']
    
    def validate(self, data):
        
        # instead of calling each required field one by one and then validating them. We shall now store all the required fields in a list and then check the data against them
        # refer to the MODEL to see which field is required
        required_fields = ['user', 'prod', 'customer_email', 'post_code', 'deliv_add', 'ship_add', 'ship_method', 'paym_id', 'paystat']
        
        missing_fields = [ field for field in required_fields if not data.get(fields)]
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        
        
        user = data.get('user')
        prod = data.get('prod')
        
        if not Product.objects.get(prod=prod):
            return serializers.ValidationError("Product Does Not exist")
        
  
        
        
        