from django.db.models import fields
from rest_framework import serializers
from .models import Tag

class TagSerializer(serializers.ModelSerializer): #최초 회원가입에서 사용될 Serializer
    class Meta:
        model = Tag
        fields = ['nameTag', 'contents']
