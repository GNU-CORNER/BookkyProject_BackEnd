from django.db.models import fields
from rest_framework import serializers
from bookky.models import TempBook

class BookPostSerializer(serializers.ModelSerializer): #API에서 불러온 정보를 Book 데이터에 인젝션을 위해서 만든 serializer
    class Meta:
        model = TempBook
        fields = ['TBID','TITLE', 'SUBTITLE','AUTHOR', 'ISBN', 'PUBLISHER', 'PRICE', 'PAGE', 'BOOK_INDEX','BOOK_INTRODUCTION', 'PUBLISH_DATE', 'Allah_BID', 'thumbnailImage','RATING', 'thumbnail', 'searchName', 'TAG']

class BookGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempBook
        fields = ['TBID', 'TITLE','AUTHOR', 'thumbnailImage', 'RATING']

class BookSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempBook
        fields = ['TBID', 'TITLE','AUTHOR','thumbnailImage','RATING','BOOK_INTRODUCTION','PUBLISH_DATE','PUBLISHER']
