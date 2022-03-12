from django.db.models import fields
from rest_framework import serializers
from .models import Book

class BookPostSerializer(serializers.ModelSerializer): #API에서 불러온 정보를 Book 데이터에 인젝션을 위해서 만든 serializer
    class Meta:
        model = Book
        fields = ['TITLE', 'VOL', 'AUTHOR', 'EA_ISBN', 'EA_ADD_CODE', 'PUBLISHER', 'PRE_PRICE', 'PAGE', 'SUBJECT', 'BOOK_TB_CNT_URL','BOOK_INTRODUCTION_URL', 'INPUT_DATE', 'UPDATE_DATE']

'''
class Book(models.Model):
    BID                     = models.BigAutoField(primary_key=True)          #Primary Key
    TITLE                   = models.CharField(max_length=50, null=False)    #책 제목
    VOL                     = models.CharField(max_length=20, null=True)     #책 권차
    AUTHOR                  = models.CharField(max_length=20, null=False)    #저자
    EA_ISBN                 = models.IntegerField(null=False)                #ISBN코드
    EA_ADD_CODE             = models.IntegerField(null=False)                #ISBN 부가 기호
    PUBLISHER               = models.CharField(max_length=20, null=False)    #발행처
    PRE_PRICE               = models.IntegerField(null=False)                #가격
    PAGE                    = models.CharField(max_length=20, null=False)    #페이지
    SUBJECT                 = models.CharField(max_length=20, null=True)     #주제(KDC대분류)
    thumbnail               = models.CharField(max_length=255, null=True)    #thumbnail API의 출력값 URL 변수명은 'TITLE_URL'
    BOOK_TB_CNT_URL         = models.CharField(null=True)                    #목차
    BOOK_INTRODUCTION_URL   = models.CharField(null=True)                    #책 소개
    BOOK_SUMMARY_URL        = models.CharField(null=True)                    #책 요약
    INPUT_DATE              = models.DateField(null=False)                   #등록날짜
    UPDATE_DATE             = models.DateField(null=False)                   #수정날짜
    Tag                     = models.CharField(max_length=100, null=False)   #태그
    Rating                  = models.DoubleField(null=False, default = 2.5)  #별점 (기본값 2.5점)
    Allah_BID               = models.IntegerField(null=False)                #알라딘 고유 책번호


'''