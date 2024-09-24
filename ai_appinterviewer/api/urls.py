from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    
    # CRUD USER links:
    path('register/', views.RegisterView.as_view(), name='register'),
    path('users/', views.UserListView.as_view(), name='users-list'),
    path('user-profile/<str:pk>', views.UserProfileView.as_view(), name='user_view'),
    path('user-profile-update/<str:pk>', views.UserUpdateView.as_view(), name= 'user_profile_update'),
    path('admin/user-profile/delete/<str:pk>', views.UserDeleteView.as_view(), name='user_profile_delete'),
    
    
    # CRUD CATEGORY links:
    path('admin/category-creation/', views.CategoryCreationView.as_view() , name = 'category_creation'),
    path('category/', views.CategoryListView.as_view(), name= 'all_category_view'),
    path('category/<str:pk>', views.CategorySingleView.as_view(), name= 'category_view'  ),
    path('admin/category-update/<str:pk>', views.CategoryUpdateView.as_view(), name= 'category_update' ),
    path('admin/category-delete/<str:pk>', views.CategoryDeleteView.as_view(), name= 'category_delete'),
    
    
    #CRUD PRODUCT links:
    path('admin/product-creation/', views.ProdCreationView.as_view(), name= 'product_creation'),
    path('product/', views.ProductListView.as_view(), name= 'product_all_view'),
    path('product/<str:pk>', views.ProductSingleView.as_view(), name= 'product_view'),
    path('admin/product-update/<str:pk>', views.ProductUpdateView.as_view(), name= 'product_update' ),
    path('admin/product-delete/<str:pk>', views.ProductDeleteView.as_view(), name= 'product_delete' ),
    
    
    # CRUD PRODUCT IMAGES links:
    path('admin/product-image-creation/', views.ProdImagesCreationView.as_view(), name= 'product_image_creation'),
    path('product-images/', views.ProdImagesListView.as_view(), name= 'product_images_view'),
    path('product-images/<str:pk>', views.ProdImagesSingleView.as_view(), name= 'product_image_view'),
    path('product-images/update/<str:pk>', views.ProductUpdateView.as_view(), name= 'product_image_update'),
    path('admin/product-images/delete/<str:pk>', views.ProductDeleteView.as_view(), name= 'product_image_delete'),
    
    
    # CRU CART links (Cart doesnot need to be deleted as its in pre-buying stage) :
    path('cart-checkout-session/', views.CartView.as_view(), name= 'cart_checkout_creation' ),
    path('admin/cart-checkout/', views.CartView.as_view(), name= 'cart_checkout_all_views'),
    path('cart-checkout/<str:pk>', views.CartView.as_view(), name= 'cart_checkout_view'),
    path('cart-checkout/update/<str:pk>', views.CartView.as_view(), name= 'cart_checkout_update'),
    path('cart-checkout/<str:pk>', views.CartView.as_view(), name= 'cart_delete'),
    path('cart-checkout/<str:pk>/cart-item/<str:item_pk>', views.CartView.as_view(), name= 'cart_delete_items'),
    
    # CART_CHECKOUT_SUCCESS & CART_CHECKOUT_FAIL LINKS:
    path('payment_success/', views.PaymentSuccessView.as_view(), name= 'payment_success'),
    path('payment_cancelled/', views.PaymentCancelledView.as_view(), name= 'payment_cancelled'),
    
    path('webhook/stripe/', views.StripeWebhookView.as_view(), name= 'Stripe webhook'),
    
    
    # CRUD ORDER
    
    
    # MISCELLANNIOUS LINKS:
    
    # USER login:
    path('login/', views.LoginView.as_view(), name='login'),
    
    # PASSWORD reset links:
    path('password_reset/', views.PasswordResetView.as_view(), name= 'password_reset'),
    path('password_reset-confirm/<str:token>', views.PasswordResetConfirmView.as_view(), name= 'password_reset_confirm'),
    
    # RANDOM FUNCTIONS links:
    path('profit-calculator/', views.ProductProfitCalculator.as_view(), name= 'product_profit_calculator'),
    path('emi-calculator/', views.EmiCalculatorView.as_view(), name= 'emi_calculator'),
    path('book-finder/', views.BookFinder.as_view(), name='book_finder'),
    
    
    
    
    
    
    
    
    
]