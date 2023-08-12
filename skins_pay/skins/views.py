from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, user_login_failed, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
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

class SkinsArr():
    def __init__(self, name, price, now_price):
        self.name = name
        self.price = price
        self.now_price = now_price

class MySKinsResult():
    def __init__(self, name, price, now_price, value):
        self.name = name
        self.price = price
        self.percent = (now_price - price) / price * 100
        self.impact = now_price / 100 * 87 - price
        self.value = value
        self.now_price = now_price

def main_page(request):
    return render(request, "main_page.html")

def market(request):
    #url = "https://steamcommunity.com/market/priceoverview/?currency=5&country=ru&appid=730&market_hash_name=Sticker%20|%20Gen.G%20|%202020%20RMR&format=json"
    url = "https://steamcommunity.com/inventory/" + str(ProfileSteam.objects.get(user=request.user).id64) + "/730/2?count=5000"
    #response = requests.get(url)

    items = []

    values = []

    data = cache.get(ProfileSteam.objects.get(user=request.user).id64)

    if not data:
        data = requests.get(url).json()
        cache.set(ProfileSteam.objects.get(user=request.user).id64, data, 1200)
    
    descriptions = data.get('descriptions')
    assets  = data.get('assets')

    address = '103.155.217.156'
    port = '41471'

    proxies = {
        'http': f'http://{address}:{port}',
        'https': f'https://{address}:{port}',
    }

    for i in assets:
        assetid = int(str(i.get('assetid')))
        classid = i.get('classid')

        price = cache.get(classid)

        if not price:
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
                cache.set(classid, price, 1200)
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
                Skin.objects.create(name=name, price=price, assetid=assetid, user=request.user)

                return render(request, "success.html", {'res':'Предмет успешно добавлен'})
            except:
                return render(request, "new_item.html", {'assetid':assetid, 'name':name, 'error':"Ошибка ввода цены"})

def my_skins(request):
    items = []
    skins_arr = []

    url = "https://steamcommunity.com/inventory/" + str(ProfileSteam.objects.get(user=request.user).id64) + "/730/2?count=5000"

    error = ""
    
    data = cache.get(ProfileSteam.objects.get(user=request.user).id64)

    if not data:
        data = requests.get(url).json()
        cache.set(ProfileSteam.objects.get(user=request.user).id64, data, 1200)

    assets = data.get('assets')
    desc = data.get('descriptions')

    class_ides = []
    assets_ides = []

    for i in assets:
        assets_ides.append(int(str(i.get('assetid'))))
        class_ides.append(int(str(i.get('classid'))))

    if Skin.objects.filter(user=request.user).exists():
        for i in Skin.objects.filter(user=request.user):
            try:
                price = cache.get(i.name)

                if not price:
                    url1 = "https://steamcommunity.com/market/priceoverview/?currency=5&country=ru&appid=730&market_hash_name=" + i.name + "&format=json"

            
                    resp = requests.get(url=url1)
                    data2 = resp.json()

                    low_price = str(data2.get('lowest_price'))
                    low_price = low_price[:-5]
                    low_price = low_price.replace(",", ".")

                    price = float(low_price)
                    cache.set(i.name, price, 1200)

                if i.assetid not in assets_ides:
                    Skin.objects.get(assetid=i.assetid).delete()
                else:
                    skins_arr.append(SkinsArr(i.name, i.price, now_price=price))

            except:
                pass
    else:
        error = 'У вас нет отслеживаеымх предметов'
    
    for i in skins_arr:
        result = list(filter(lambda item: item.name == i.name and item.price == i.price, items))
        if not result:
            items.append(MySKinsResult(i.name, i.price, i.now_price, value=len(list(filter(lambda item: item.name == i.name and item.price == i.price, skins_arr)))))
    data = {
        'error' : error,
        'descriptions' : items
    }

    return render(request, "my_skins.html", data)

def page_update(request, assetid):
    name = Skin.objects.get(assetid=assetid).name
    url = "https://steamcommunity.com/inventory/" + str(ProfileSteam.objects.get(user=request.user).id64) + "/730/2?count=5000"
    
    data = cache.get(ProfileSteam.objects.get(user=request.user).id64)

    if not data:
        data = requests.get(url).json()
        cache.set(ProfileSteam.objects.get(user=request.user).id64, data, 1200)

    assets = data.get('assets')
    desc = data.get('descriptions')

    check_item = False
    classid = 0
    for i in desc:
        name1 = i.get('market_hash_name')
        if name1 == name:
            check_item = True
            classid = int(i.get('classid'))

            break
    
    new_assetid = 0

    if check_item == True:
        for i in assets:
            if int(i.get('classid')) == classid:
                if not Skin.objects.filter(assetid=int(i.get('assetid'))).exists():
                    new_assetid = int(i.get('assetid'))

                    break
        else:
            check_item = False
    
    return render(request, "page_update.html", {'assetid':assetid, 'new_assetid':new_assetid, 'check_item':check_item})

def update(request, assetid, new_assetid):
    skin = Skin.objects.get(user=request.user, assetid=assetid)
    skin.assetid = new_assetid
    skin.save()

    return redirect("my_skins")

def delete_skin(request, assetid):
    Skin.objects.get(user=request.user, assetid=assetid).delete()

    return redirect("my_skins")

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