from django.db.models import fields
from rest_framework import serializers
from .models import FavoriteBook

class FavoriteBookSerializer(serializers.ModelSerializer): #갱신 토큰 Serializer
    class Meta:
        model = FavoriteBook
        fields = ['BID','UID']
        