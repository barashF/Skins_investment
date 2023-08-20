"""
URL configuration for skins_pay project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include, re_path
from skins.views import *
from django.conf import settings
from django.conf.urls.static import static
from skins.views import *
from rest_framework import routers


urlpatterns = [
    path('', main_page, name="main_page"),
    path('admin/', admin.site.urls),
    path('api/v1/my_skins/', Api_my_skins.as_view()),
    path('api/v1/skins/', SkinsView.as_view()),
    path('api/v1/skins/<int:id64>/', SkinsView.as_view()),
    path('api/v1/auth/', include("djoser.urls")),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('market/', include("skins.urls"))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)