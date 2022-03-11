from django.db import models

#전체적인 컬럼 이름은 API의 출력값 그대로 정했음
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


    

class User(models.Model): 
    '''DB column'''
    UID                     = models.BigAutoField(primary_key=True)
    #PID                     = models.ManyToManyField('Product')
    pwToekn                 = models.CharField(max_length=255, null=False)
    email                   = models.EmailField(max_length=100, null=False)
    name                    = models.CharField(max_length=50, null=False)
    address                 = models.CharField(max_length=100, null=False)
    phone                   = models.CharField(max_length=20, null=False)
    nickname                = models.CharField(max_length=10, null=False, default="ABC")
    pushToken               = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.nickname

