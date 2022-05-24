from django.db.models import fields
from rest_framework import serializers
from bookky.models import TagModel

class TagSerializer(serializers.ModelSerializer): #최초 회원가입에서 사용될 Serializer
    class Meta:
        model = TagModel
        fields = ['TMID','nameTag','searchName']
