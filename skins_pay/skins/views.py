from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, user_login_failed, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from rest_framework import generics, viewsets
from .models import Skin, ProfileSteam
from .sirializers import SkinSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import stem
from stem import Signal
from stem.control import Controller
import time
import json
from steamauth import auth, get_uid


class ResultSkin():
    def __init__(self, name, reg, price, now_price, assetid):
        self.name = name
        self.reg = reg

        if reg:
            self.price = price
            self.percent = (now_price - price) / price * 100
            self.impact = now_price / 100 * 87 - price
        self.assetid = assetid

        self.now_price = now_price

def main_page(request):
    return render(request, "main_page.html")

def market(request):
    #url = "https://steamcommunity.com/market/priceoverview/?currency=5&country=ru&appid=730&market_hash_name=Sticker%20|%20Gen.G%20|%202020%20RMR&format=json"
    url = "https://steamcommunity.com/inventory/76561198810795131/730/2?count=5000"
    #response = requests.get(url)

    items = []

    values = []

    with open('C:/Users/artem/Desktop/project drf/skins_pay/skins/j_skins.json', encoding='utf-8') as f:
        data = json.load(f)
    
    descriptions = data.get('descriptions')
    assets  = data.get('assets')

    hash_price = {}

    address = '103.155.217.156'
    port = '41471'

    proxies = {
        'http': f'http://{address}:{port}',
        'https': f'https://{address}:{port}',
    }

    for i in assets:
        assetid = int(str(i.get('assetid')))
        classid = i.get('classid')
        
        if classid in hash_price.keys():
            price = hash_price[classid]
        else:
            name = ""
            for j in descriptions:
                if j.get('classid') == classid:
                    name = j.get('market_hash_name')
                    break

            url1 = "https://steamcommunity.com/market/priceoverview/?currency=5&country=ru&appid=730&market_hash_name=" + name + "&format=json"

            
            resp = requests.get(url=url1)
            data2 = resp.json()
            try:
                low_price = str(data2.get('lowest_price'))
                low_price = low_price[:-5]
                low_price = low_price.replace(",", ".")

                price = float(low_price)
                hash_price[classid] = price
            except:
                continue
        
        name = ""
        for j in descriptions:
            if j.get('classid') == classid:
                name = j.get('market_hash_name')
                break

        if Skin.objects.filter(assetid=assetid).exists():
            items.append(ResultSkin(name, True, Skin.objects.get(assetid=assetid).price, price, ""))
        else:
            items.append(ResultSkin(name, False, 0, now_price=price, assetid=int(assetid)))

    return render(request, 'market.html', {'descriptions':items})

def new_item(request, assetid, name):
    return render(request, "new_item.html", {'assetid':assetid, 'name':name, 'error':""})

def add_item(request, assetid, name):
    if request.method == "GET":
        if Skin.objects.filter(assetid=assetid).exists():
            return render(request, "new_item.html", {'assetid':assetid, 'name':name, 'error':"Данный предмет уже зарегистрирован"})
        else:
            my_input_value = str(request.GET.get('price'))
            
            try:
                price = float(my_input_value.replace(",", "."))
                Skin.objects.create(name=name, price=price, assetid=assetid)

                return render(request, "success.html", {'res':'Предмет успешно добавлен'})
            except:
                return render(request, "new_item.html", {'assetid':assetid, 'name':name, 'error':"Ошибка ввода цены"})

def login(request):
    return auth('/callback')

def login_callback(request):
    steam_uid = int(get_uid(request.GET))
    if steam_uid is None:

        return render(request, "success.html", {'res':'ошибка'})
    else:
        if ProfileSteam.objects.filter(id64=steam_uid).exists():
            user = authenticate(username=str(steam_uid), password="123456789GUSTAV")

            if user is not None:
                login(user)
            else:
                print("ошибка")
        else:
            user = User.objects.create(username=str(steam_uid))
            user.set_password("123456789GUSTAV")
            user.save()

            ProfileSteam.objects.create(user=user, id64=steam_uid)

            user = authenticate(username=str(steam_uid), password="123456789GUSTAV")
            if user is not None:
                login(user)
            else:
                print("ошибка")

        return render(request, "success.html", {'res':steam_uid})

class SkinViewSet(viewsets.ModelViewSet):
    queryset = Skin.objects.all()
    serializer_class = SkinSerializer

# class SkinAPIList(generics.ListCreateAPIView):
#     queryset = Skin.objects.all()
#     serializer_class = SkinSerializer

# class SkinAPIUpdate(generics.UpdateAPIView):
#     queryset = Skin.objects.all()
#     serializer_class = SkinSerializer

# class SkinAPIDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Skin.objects.all()
#     serializer_class = SkinSerializer
    
# class SkinAPIView(APIView):

#     def get(self, request):
#         lst = Skin.objects.all()
#         return Response({'post': SkinSerializer(lst, many=True).data})

#     def post(self, request):
#         serializer = SkinSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response({'post': serializer.data})

#     def put(self, request, *args, **kwargs):
#         pk = kwargs.get("pk", None)

#         if not pk:
#             return Response({'error':'not found'})
        
#         try:
#             instance = Skin.objects.get(pk=pk)
#         except:
#             return Response({'error':'not found'})
        
#         serializer = SkinSerializer(data=request.data, instance=instance)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response({'post':serializer.data})
    
#     def delete(self, request, *args, **kwargs):
#         pk = kwargs.get("pk", None)

#         if not pk:
#             return Response({'error':'not found'})
        
#         Skin.objects.get(pk=pk).delete()


# class SkinAPIView(generics.ListAPIView):
#     queryset = Skin.objects.all()
#     serializer_class = SkinSerializer