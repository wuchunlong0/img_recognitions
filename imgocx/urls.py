"""imgocx URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from  mysite import views
from django.views.generic import RedirectView
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    
    url(r'^$', views.distinguish_img_str, name="distinguish_img_str"),    
    url(r'^distinguish_img/', views.distinguish_img, name="distinguish_img"),     

    url(r'^wx_uploadFile/', views.wx_uploadFile, name="wx_uploadFile"),     
    
    url(r'^index/', views.index, name="index"),
    #url(r'^$', RedirectView.as_view(url='/home/index/')),
    
    url(r'^test_img/', views.test_img, name="test_img"),    
    url(r'^unit_test/', views.unit_test, name="unit_test"),    
    

 
    url(r'^identity_recognition/', views.identity_recognition, name="identity_recognition"),

    url(r'^test_array/', views.test_array, name="test_array"),
    url(r'^get_numimg/', views.get_numimg, name="get_numimg"),
    url(r'^test_English_img/', views.test_English_img, name="test_English_img"),


]
