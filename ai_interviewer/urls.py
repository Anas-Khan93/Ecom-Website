
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse


def home(request):
    return HttpResponse("WELCOME TO THE HOME PAGE")


urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('api/', include("ai_appinterviewer.api.urls")),
    path('', home, name='home'), # this line handles the root path
    
]
