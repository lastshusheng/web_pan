"""web_disk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from disk import views
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.views.static import serve
from django.views.generic import RedirectView

urlpatterns = [
    url('^$',RedirectView.as_view(url='index/')),
    url('^admin/', admin.site.urls),
    url('^login/', views.login),
    url('^logout/', views.logout),
    url('^index/', views.index),
    url('^get_dir_list/',views.get_dir_list),
    url('^mkdir/',views.user_mkdir),
    url('^del_dir/',views.del_dir),
    url('^query_file/',views.query_file),
    url('^upload/',views.upload_file),
    url('^del_file/',views.del_file),
    url('^download/',views.download_file),
]
