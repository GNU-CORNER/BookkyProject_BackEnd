from django.db.models import fields
from rest_framework import serializers
from bookky.models import FavoriteBook

class FavoriteBookSerializer(serializers.ModelSerializer): #갱신 토큰 Serializer
    class Meta:
        model = FavoriteBook
        fields = ['TBID','UID']
        