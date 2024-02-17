from django.contrib import admin
from django.urls import path, include
from django.conf.urls import *  # Add this import

from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('creditapp.urls')), 
    path('auth/', include('djoser.urls')),
]  
