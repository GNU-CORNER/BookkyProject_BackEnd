from django.db.models import fields
from rest_framework import serializers
from .models import Book

class BookPostSerializer(serializers.ModelSerializer): #API에서 불러온 정보를 Book 데이터에 인젝션을 위해서 만든 serializer
    class Meta:
        model = Book
        fields = ['TITLE', 'SUBTITLE','VOL', 'AUTHOR', 'ISBN', 'PUBLISHER', 'PRICE', 'PAGE', 'SUBJECT', 'BOOK_INDEX','BOOK_INTRODUCTION','BOOK_SUMMARY' ,'INPUT_DATE']

'''
    BID                     = models.BigAutoField(primary_key=True)          #Primary Key
    TITLE                   = models.CharField(max_length=50, null=False)    #책 제목
    SUBTITLE                = models.CharField(max_length=50, null=True)   
    VOL                     = models.CharField(max_length=20, null=True)     #책 권차
    AUTHOR                  = models.CharField(max_length=20, null=False)    #저자
    ISBN                    = models.CharField(max_length=20, null=False)    #ISBN코드             데이터 인젝트시에 String을 Integer로 바꿔서 넣어야함
    PUBLISHER               = models.CharField(max_length=20, null=False)    #발행처
    PRICE                   = models.IntegerField(null=True)                 #가격                 데이터 인젝트시에 String을 Integer로 바꿔서 넣어야함
    PAGE                    = models.CharField(max_length=20, null=True)     #페이지
    SUBJECT                 = models.CharField(max_length=20, null=True)     #주제(KDC대분류)
    thumbnail               = models.CharField(max_length=255, null=True)    #thumbnail API의 출력값 URL 변수명은 'TITLE_URL'
    BOOK_INDEX              = models.CharField(null=True)                    #목차
    BOOK_INTRODUCTION       = models.CharField(null=True)                    #책 소개
    BOOK_SUMMARY            = models.CharField(null=True)                    #책 요약
    PUBLISH_DATE            = models.DateField(null=False)                   #등록날짜
    UPDATE_DATE             = models.DateField(null=True)                    #수정날짜
    TAG                     = models.CharField(max_length=100, null=False)   #태그
    RATING                  = models.DoubleField(null=False, default = 2.5)  #별점 (기본값 2.5점)
    Allah_BID               = models.IntegerField(null=False)                #알라딘 고유 책번호

'''