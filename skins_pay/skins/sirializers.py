from rest_framework import serializers, generics
from .models import Skin
from rest_framework.renderers import JSONRenderer

class SkinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skin
        fields = "__all__"

    name = serializers.CharField()
    price = serializers.FloatField()
    assetid = serializers.IntegerField()
    user = serializers.IntegerField()

        

