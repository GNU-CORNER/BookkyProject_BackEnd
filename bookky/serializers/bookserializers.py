from django.db.models import fields
from rest_framework import serializers
from bookky.models import Book

class BookPostSerializer(serializers.ModelSerializer): #API에서 불러온 정보를 Book 데이터에 인젝션을 위해서 만든 serializer
    class Meta:
        model = Book
        fields = ['BID','TITLE', 'SUBTITLE','AUTHOR', 'ISBN', 'PUBLISHER', 'PRICE', 'PAGE', 'BOOK_INDEX','BOOK_INTRODUCTION', 'PUBLISH_DATE', 'Allah_BID', 'thumbnailImage']

class BookGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['BID', 'TITLE','AUTHOR', 'thumbnailImage']