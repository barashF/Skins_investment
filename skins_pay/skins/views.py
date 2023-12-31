from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, user_login_failed, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
from rest_framework import generics, viewsets, authentication
from rest_framework.permissions import *
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
from rest_framework.decorators import action, api_view


class ResultSkin():
    def __init__(self, name, reg, price, now_price, assetid):
        self.name = name
        self.reg = reg

        if reg:
            self.price = price
            self.percent = round((now_price - price) / price * 100, 2)
            self.impact = round(now_price / 100 * 87 - price, 2)
        else:
            self.price = "-"
            self.percent = "-"
            self.impact = "-"

        self.assetid = assetid
        self.now_price = now_price

        def to_dict(self):
            info = {
                "name":self.name,
                "price":self.price,
                "now_price":self.now_price,
                "percent":self.percent,
                "impact":self.impact
            }

class SkinsArr():
    def __init__(self, name, price, now_price):
        self.name = name
        self.price = price
        self.now_price = now_price

class MySKinsResult():
    def __init__(self, name, price, now_price, value):
        self.name = name
        self.price = price
        self.percent = round((now_price - price) / price * 100, 2)
        self.impact = round((now_price / 100 * 87 - price) * value, 2)
        self.value = value
        self.now_price = now_price
    
    def to_dict(self):
        info = {
            "name":self.name,
            "price":self.price,
            "percent":self.percent,
            "impact":self.impact,
            "value":self.value,
            "now_price":self.now_price
        }

        return info

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

                return redirect("my_skins")
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

    start_cost = 0
    cost = 0

    percent_def = 0

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

                start_cost += i.price
                cost += (price / 100 * 87 ) 

            except:
                pass
        percent_def = round(((cost - start_cost)/start_cost)*100, 2)
    else:
        error = 'У вас нет отслеживаеымх предметов'
    
    for i in skins_arr:
        result = list(filter(lambda item: item.name == i.name and item.price == i.price, items))
        if len(result) == 0:
            items.append(MySKinsResult(i.name, i.price, i.now_price, value=len(list(filter(lambda item: item.name == i.name and item.price == i.price, skins_arr)))))
    
    impact = round((cost - start_cost), 2)
    data = {
        'error' : error,
        'descriptions' : items,
        'cost' : round(cost, 2),
        'impact' : impact,
        'percent_def' : percent_def
    }

    return render(request, "my_skins.html", data)

def page_update(request, name, price):
    url = "https://steamcommunity.com/inventory/" + str(ProfileSteam.objects.get(user=request.user).id64) + "/730/2?count=5000"

    data = cache.get(ProfileSteam.objects.get(user=request.user).id64)

    if not data:
        data = requests.get(url).json()
        cache.set(ProfileSteam.objects.get(user=request.user).id64, data, 1200)

    assets = data.get('assets')
    desc = data.get('descriptions')

    classid = 0
    for i in desc:
        if str(i.get('market_hash_name')) == name:
            classid = int(i.get('classid'))
            break

    counter = 0
    for i in assets:
        if int(i.get('classid')) == classid:
            if len(Skin.objects.filter(assetid=int(i.get('assetid')))) == 0:
                counter += 1

    return render(request, "page_update.html", {'name':name, 'price':price, 'counter':counter, 'error':''})

def update(request, name, price):
    if request.method == 'GET':
        price = float(price)

        skins = Skin.objects.filter(user=request.user, name=name, price=price)
        value_str = str(request.GET.get('value'))
        value = int(value_str)
        url = "https://steamcommunity.com/inventory/" + str(ProfileSteam.objects.get(user=request.user).id64) + "/730/2?count=5000"

        data = cache.get(ProfileSteam.objects.get(user=request.user).id64)

        if not data:
            data = requests.get(url).json()
            cache.set(ProfileSteam.objects.get(user=request.user).id64, data, 1200)

        assets = data.get('assets')
        desc = data.get('descriptions')

        try:
            classid = 0
            for i in desc:
                if str(i.get('market_hash_name')) == name:
                    classid = int(i.get('classid'))
                    break
        
            asset_ides = []

            counter = 0
            for i in assets:
                if int(i.get('classid')) == classid:
                    try:
                        skin = Skin.objects.get(assetid=int(i.get('assetid')))
                    except Skin.DoesNotExist:
                        counter += 1
                        asset_ides.append(int(i.get('assetid')))
        except:
            return render(request, "page_update.html", {'name':name, 'price':price, 'counter':counter, 'error':'Неверный формат ввода'})

        if value > counter:
            return render(request, "page_update.html", {'name':name, 'price':price, 'counter':counter, 'error':'Введённое число больше, чем количество незарегистрированных предметов в инвентаре'})
    
        for i in range(value):
            Skin.objects.create(user=request.user, name=name, price=price, assetid=asset_ides[i])

    return redirect("my_skins")

def delete_skin(request, assetid):
    Skin.objects.get(user=request.user, assetid=assetid).delete()

    return redirect("my_skins")

def mlogin(request):
    return auth('/callback')

def login_callback(request):
    steam_uid = int(get_uid(request.GET))
    if steam_uid is None:

        return render(request, "success.html", {'res':'ошибка'})
    else:
        if ProfileSteam.objects.filter(id64=steam_uid).exists():
            user = authenticate(username=ProfileSteam.objects.get(id64=steam_uid).user.username, password="123456789GUSTAV")

            if user is not None:
                login(request, user)
            else:
                print("ошибка")
        else:
            user = User.objects.create(username=str(steam_uid))
            user.set_password("123456789GUSTAV")
            user.save()

            ProfileSteam.objects.create(user=user, id64=steam_uid)

            user = authenticate(username=str(steam_uid), password="123456789GUSTAV")

            if user is not None:
                login(request, user)
            else:
                print("ошибка")

        return render(request, "success.html", {'res':steam_uid})

def api_login(request, id64):
    steam_uid = id64
    if ProfileSteam.objects.filter(id64=steam_uid).exists():
        user = authenticate(username=ProfileSteam.objects.get(id64=steam_uid).user.username, password="123456789GUSTAV")

        if user is not None:
            login(request, user)
        else:
            print("ошибка")
    else:
        user = User.objects.create(username=str(steam_uid))
        user.set_password("123456789GUSTAV")
        user.save()

        ProfileSteam.objects.create(user=user, id64=steam_uid)

        user = authenticate(username=str(steam_uid), password="123456789GUSTAV")

        if user is not None:
            login(request, user)
        else:
            print("ошибка")

class Api_inventory(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        id64 = int(request.data.get("steamid"))
        
        url = "https://steamcommunity.com/inventory/" + str(id64) + "/730/2?count=5000"

        data = cache.get(id64)

        items = []

        if not data:
            data = requests.get(url).json()
            cache.set(id64, data, 1200)

        assets = data.get('assets')
        desc = data.get('descriptions')

        for i in assets:
            assetid = int(i.get("assetid"))
            
            name = ""
            for j in desc:
                if int(j.get("classid")) == int(i.get("classid")):
                    name = j.get("market_hash_name")
                    price = cache.get(j.get("market_hash_name"))

                    if not price:
                        url1 = "https://steamcommunity.com/market/priceoverview/?currency=5&country=ru&appid=730&market_hash_name=" + j.get("market_hash_name") + "&format=json"

                        resp = requests.get(url=url1)
                        data2 = resp.json()

                        low_price = str(data2.get('lowest_price'))
                        low_price = low_price[:-5]
                        low_price = low_price.replace(",", ".")

                        price = float(low_price)
                        cache.set(j.get("market_hash_name"), price, 1200)
                    
                    break

            if Skin.objects.filter(user=ProfileSteam.objects.get(id64=id64).user, assetid=assetid).exists():
                items.append(MySKinsResult(name=name, reg=True, price=Skin.objects.get(assetid=assetid).price, now_price=price, assetid=assetid))
            else:
                items.append(MySKinsResult(name=name, reg=False, now_price=price, assetid=assetid))
        
        
        data = {
            items:json.dumps(list(i.to_dict() for i in items))
        }
        
        return Response(data)

class Api_my_skins(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        id64 = int(request.data.get("steamid"))
        
        url = "https://steamcommunity.com/inventory/" + str(id64) + "/730/2?count=5000"

        data = cache.get(id64)

        if not data:
            data = requests.get(url).json()
            cache.set(id64, data, 1200)

        assets = data.get('assets')
        desc = data.get('descriptions')
        
        items = []
        list_assets = []
        list_classides = []

        for i in assets:
            list_assets.append(int(i.get("assetid")))
            list_classides.append(int(i.get("classid")))
        
        skins_arr = []
        start_cost = 0
        cost = 0
        percent_def = 0

        error = ''

        if Skin.objects.filter(user=ProfileSteam.objects.get(id64=id64).user).exists():
            for i in Skin.objects.filter(user=ProfileSteam.objects.get(id64=id64).user):
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

                    if i.assetid not in list_assets:
                        Skin.objects.get(assetid=i.assetid).delete()
                    else:
                        skins_arr.append(SkinsArr(i.name, i.price, now_price=price))

                    start_cost += i.price
                    cost += (price / 100 * 87 ) 

                except:
                    pass
            percent_def = round(((cost - start_cost)/start_cost)*100, 2)
        else:
            error = 'У вас нет зарегистрированных инвестиций'

        for i in skins_arr:
            result = list(filter(lambda item: item.name == i.name and item.price == i.price, items))
            if len(result) == 0:
                my_skin_result = MySKinsResult(i.name, i.price, i.now_price, value=len(list(filter(lambda item: item.name == i.name and item.price == i.price, skins_arr))))
                
                items.append(my_skin_result)
    
        impact = round((cost - start_cost), 2)
        
        data = {
            'error' : error,
            'items' : json.dumps(list(i.to_dict() for i in items)),
            'cost' : round(cost, 2),
            'impact' : impact,
            'percent_def' : percent_def
        }

        return Response(data)

class SkinsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        id64 = int(request.data.get("steamid"))
        skins = Skin.objects.filter(user=ProfileSteam.objects.get(id64=id64).user)
        
        return Response(json.dumps(list(skins.values())))

    def post(self, request):
        serializer = SkinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_skin = Skin.objects.create(name=request.data.get("name"), price=request.data.get("price"), assetid=request.data.get("assetid"), user=ProfileSteam.objects.get(id64=request.data.get("user")).user)

        return Response({'post':serializer.data})
    
    def put(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)

        try:
            instance = Skin.objects.get(pk=pk)
        except:
            return Response({"error": "Object does not exists"})
        
        serializer = SkinSerializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"post": serializer.data})
    
    def delete(self, request, *args, **kwargs):
        assetid = request.data.get("assetid", None)
        if not assetid:
            return Response({"error": "Method DELETE not allowed"})
 
        Skin.objects.get(assetid=assetid).delete()
 
        return Response({"post": "delete post " + str(assetid)})