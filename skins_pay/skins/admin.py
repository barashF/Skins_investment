from django.contrib import admin
from .models import Skin, Type_gun, ProfileSteam

class SkinsAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "price")
    search_fields = ["name",]

class Type_gunAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

class ProfileSteamAdmin(admin.ModelAdmin):
    list_display = ("id64", "user")

admin.site.register(Skin, SkinsAdmin)
admin.site.register(Type_gun, Type_gunAdmin)
admin.site.register(ProfileSteam, ProfileSteamAdmin)