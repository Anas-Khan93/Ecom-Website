from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import RegisterView, LoginView, PasswordResetView, PasswordResetConfirmView

urlpatterns=[
    
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('password_reset/',PasswordResetView.as_view(), name= 'password_reset'),
    path('password_reset-confirm/<str:token>', PasswordResetConfirmView.as_view(), name= 'password_reset_confirm')
    
    
]