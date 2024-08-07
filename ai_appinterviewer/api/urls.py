from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    
    path('password_reset/', views.PasswordResetView.as_view(), name= 'password_reset'),
    path('password_reset-confirm/<str:token>', views.PasswordResetConfirmView.as_view(), name= 'password_reset_confirm'),
    
    path('profit-calculator/', views.ProductProfitCalculator.as_view(), name= 'product_profit_calculator'),
    path('emi-calculator/', views.EmiCalculatorView.as_view(), name= 'emi_calculator'),
    path('book-finder/', views.BookFinder.as_view(), name='book_finder'),
    
    path('admin/category-creation/', views.CategoryView.as_view(), name = 'category_name'),
    path('user-profile/<str:pk>', views.UserProfileView.as_view(), name='user_view'),
    path('users/', views.UserListView.as_view(), name='users-list'),
    path('user-profile-update/<str:pk>', views.UserUpdateView.as_view(), name= 'user_profile_update'),
    
    path('admin/user-profile/delete/<str:pk>', views.UserDeleteView.as_view(), name='user_profile_delete')
    
]