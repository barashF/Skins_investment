from django.urls import path
from . import views

urlpatterns = [
    path('', views.market, name="market"),
    path('my_skins/', views.my_skins, name="my_skins"),
    path('login/', views.mlogin, name="mlogin"),
    path('callback/', views.login_callback, name="mcallback"),
    path('page_update/<str:name>/<str:price>', views.page_update, name="page_update"),
    path('update/<str:name>/<str:price>/', views.update, name="update"),
    path('new_item/<int:assetid>/<str:name>', views.new_item, name="new_item"),
    path('add_item/<int:assetid>/<str:name>', views.add_item, name="add_item"),
]