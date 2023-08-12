from django.urls import path
from . import views

urlpatterns = [
    path('', views.market, name="market"),
    path('my_skins/', views.my_skins, name="my_skins"),
    path('login/', views.login, name="mlogin"),
    path('callback/', views.login_callback, name="mcallback"),
    path('page_update/<int:assetid>/', views.page_update, name="page_update"),
    path('delete_skin/<int:assetid>/', views.page_update, name="delete_skin"),
    path('update/<int:assetid>/<int:new_assetid>/', views.update, name="update"),
    path('new_item/<int:assetid>/<str:name>', views.new_item, name="new_item"),
    path('add_item/<int:assetid>/<str:name>', views.add_item, name="add_item"),
]