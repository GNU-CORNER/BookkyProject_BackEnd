from django.db import models

#전체적인 컬럼 이름은 API의 출력값 그대로 정했음
class Book(models.Model):
    BID                     = models.BigAutoField(primary_key=True)                         #Primary Key
    TITLE                   = models.CharField(max_length=50, null=False)                   #책 제목
    SUBTITLE                = models.CharField(max_length=50, null=True)                    #책 부제
    AUTHOR                  = models.CharField(max_length=20, null=False)                   #저자
    ISBN                    = models.CharField(max_length=20, null=False)                   #ISBN코드             데이터 인젝트시에 String을 Integer로 바꿔서 넣어야함
    PUBLISHER               = models.CharField(max_length=20, null=False)                   #발행처
    PRICE                   = models.CharField(max_length=30, null=True)                                #가격                 데이터 인젝트시에 String을 Integer로 바꿔서 넣어야함
    PAGE                    = models.CharField(max_length=20, null=True)                    #페이지
    thumbnail               = models.CharField(max_length=255, null=True)                   #thumbnail API의 출력값 URL 변수명은 'TITLE_URL'
    BOOK_INDEX              = models.CharField(max_length=255, null=True)                   #목차
    BOOK_INTRODUCTION       = models.CharField(max_length=255, null=True)                   #책 소개
    PUBLISH_DATE            = models.DateField(null=False)                                  #등록날짜
    TAG                     = models.ArrayField(models.IntegerField(null=True), size = 50)  #태그
    RATING                  = models.FloatField(null=False, default = 2.5)                  #별점 (기본값 2.5점)
    Allah_BID               = models.CharField(max_length=30, null=True)                    #알라딘 고유 책번호
    
    def __str__(self):
        return self.TITLE

    

class User(models.Model): 
    '''DB column'''
    UID                     = models.BigAutoField(primary_key=True)                         #Primary Key
    email                   = models.EmailField(max_length=100, null=False)                 #이메일
    pwToekn                 = models.CharField(max_length=255, null=False)                  #이메일 인증 토큰 혹은 인증 Refresh Token값이 들어갈 것 같다.
    nickname                = models.CharField(max_length=10, null=False, default="북아무개") #닉네임 (기본값 '북아무개')
    thumbnail               = models.CharField(max_length=255, null=True)                   #프로필 이미지
    tag_array               = models.ArrayField(models.IntegerField(null=True), size=50)    #Tag Array 정수형 배열로 선언함 크기 50
    pushNoti                = models.BooleanField(null=False, default=False)                #푸쉬 알림 승인 값
    pushToken               = models.CharField(max_length=255, null=True)                   #푸쉬 토큰 저장용

    def __str__(self):
        return self.nickname

