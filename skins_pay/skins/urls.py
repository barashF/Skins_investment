from django.urls import path
from . import views

urlpatterns = [
    path('', views.market, name="market"),
    path('login/', views.login, name="mlogin"),
    path('callback/', views.login_callback, name="mcallback"),
    path('new_item/<int:assetid>/<str:name>', views.new_item, name="new_item"),
    path('add_item/<int:assetid>/<str:name>', views.add_item, name="add_item"),
]