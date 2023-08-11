from rest_framework import serializers, generics
from .models import Skin
from rest_framework.renderers import JSONRenderer

class SkinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skin
        fields = "__all__"

    def create(self, validated_data):
        return Skin.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.type_gun = validated_data.get("type_gun", instance.type_gun)
        instance.float_gun = validated_data.get("float_gun", instance.float_gun)
        instance.save()

        return instance

