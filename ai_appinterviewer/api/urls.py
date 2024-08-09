from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    
    #CRUD user links:
    path('register/', views.RegisterView.as_view(), name='register'),
    path('users/', views.UserListView.as_view(), name='users-list'),
    path('user-profile/<str:pk>', views.UserProfileView.as_view(), name='user_view'),
    path('user-profile-update/<str:pk>', views.UserUpdateView.as_view(), name= 'user_profile_update'),
    path('admin/user-profile/delete/<str:pk>', views.UserDeleteView.as_view(), name='user_profile_delete'),
    
    #CRUD category links:
    path('admin/category-creation/', views.CategoryCreationView.as_view() , name = 'category_creation'),
    path('category/', views.CategoryListView.as_view(), name= 'all_category_view'),
    path('category/<str:pk>', views.CategorySingleView.as_view(), name= 'category_view'  ),
    path('admin/category-update/<str:pk>', views.CategoryUpdateView.as_view(), name= 'category_update' ),
   #path('category-deletion/<str:pk>', views.CategoryDeleteView.as_view(), name= 'category_delete' ),
    
    #USER login links:
    path('login/', views.LoginView.as_view(), name='login'),
    
    # PASSWORD reset links:
    path('password_reset/', views.PasswordResetView.as_view(), name= 'password_reset'),
    path('password_reset-confirm/<str:token>', views.PasswordResetConfirmView.as_view(), name= 'password_reset_confirm'),
    
    # RANDOM FUNCTIONS links:
    path('profit-calculator/', views.ProductProfitCalculator.as_view(), name= 'product_profit_calculator'),
    path('emi-calculator/', views.EmiCalculatorView.as_view(), name= 'emi_calculator'),
    path('book-finder/', views.BookFinder.as_view(), name='book_finder'),
    
    
    
    
    
    
    
    
    
]