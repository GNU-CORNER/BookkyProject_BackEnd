import email
from email.policy import default
from django.contrib.postgres.fields import ArrayField
from django.db import models


#전체적인 컬럼 이름은 API의 출력값 그대로 정했음
class Book(models.Model):
    BID                     = models.BigAutoField(primary_key=True)                         #Primary Key
    TITLE                   = models.CharField(max_length=255, null=False)                   #책 제목
    SUBTITLE                = models.CharField(max_length=255, null=True)                    #책 부제
    AUTHOR                  = models.CharField(max_length=100, null=True, blank=True)                   #저자
    ISBN                    = models.CharField(max_length=30, null=True, blank=True)                   #ISBN코드             데이터 인젝트시에 String을 Integer로 바꿔서 넣어야함
    PUBLISHER               = models.CharField(max_length=255, null=True, blank=True)                   #발행처
    PRICE                   = models.CharField(max_length=30, null=True)                    #가격                 데이터 인젝트시에 String을 Integer로 바꿔서 넣어야함
    PAGE                    = models.CharField(max_length=20, null=True)                    #페이지
    thumbnail               = models.CharField(max_length=255, null=True)                   #thumbnail API의 출력값 URL 변수명은 'TITLE_URL'
    BOOK_INDEX              = models.TextField(verbose_name='목차', null=True, blank=True)                          #목차
    BOOK_INTRODUCTION       = models.TextField(verbose_name='소개', null=True, blank=True)                          #책 소개
    PUBLISH_DATE            = models.CharField(max_length=30, null=True)                    #등록날짜
    TAG                     = ArrayField(models.IntegerField(null=True), size = 50, null=True)         #태그
    RATING                  = models.FloatField(null=False, default = 2.5)                  #별점 (기본값 2.5점)
    Allah_BID               = models.CharField(max_length=30, null=True)                    #알라딘 고유 책번호
    thumbnailImage          = models.CharField(max_length=255, null=True)
    
    def __str__(self):
        return self.BID

    
class User(models.Model): 
    '''DB column'''
    UID                     = models.BigAutoField(primary_key=True)                         #Primary Key
    email                   = models.EmailField(max_length=100, null=False)                 #이메일
    pwToken                 = models.TextField(null=False, blank=True)                  #이메일 인증 토큰 혹은 인증 Refresh Token값이 들어갈 것 같다.
    nickname                = models.CharField(max_length=10, null=False, default="북아무개") #닉네임 (기본값 '북아무개')
    thumbnail               = models.CharField(max_length=255, null=True)                   #프로필 이미지
    tag_array               = ArrayField(models.IntegerField(null=True), size=50, null=True)           #Tag Array 정수형 배열로 선언함 크기 50
    pushNoti                = models.BooleanField(null=False, default=False)                #푸쉬 알림 승인 값
    pushToken               = models.TextField(null=True, blank=True)                       #푸쉬 토큰 저장용
    loginMethod             = models.IntegerField(default=0, null=False)                    #0 = 자체 회원가입, 1 = Github, 2 = Google, 3 = Apple
    def __str__(self):
        return self.UID


class AnyCommunity(models.Model):                                                                                           #자유게시판
    APID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    BID                     = models.ForeignKey("Book", on_delete=models.CASCADE ,null=True)                                #책 외래키
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    contents                = models.TextField(verbose_name='내용')                                                          #내용
    title                   = models.CharField(max_length=255, null=False)                                                   #제목
    postImage               = models.CharField(max_length=255, null=True)                                                   #여러개 어떻게?
    createAt                = models.DateField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateField(auto_now=True, null=False)                                                                   #수정날짜
    views                   = models.IntegerField(null=False, default = 0)                                                  #뷰
    like                    = ArrayField(models.IntegerField(null=True), null=True, size = 10000000, default = list())                                   #좋아요, 숫자는 최대

    def __str__(self):
        return self.APID


class MarketCommunity(models.Model):                                                                                        #장터게시판 자게와 동일
    MPID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    BID                     = models.ForeignKey("Book", on_delete=models.CASCADE ,null=True)                                #책 외래키
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    contents                = models.TextField(verbose_name='내용')                                                          #내용
    title                   = models.CharField(max_length=255, null=False)                                                   #제목
    postImage               = models.CharField(max_length=255, null=True)                                                   #여러개 어떻게?
    createAt                = models.DateField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateField(auto_now=True, null=False)                                                                   #수정날짜
    views                   = models.IntegerField(null=False, default = 0)                                                  #뷰
    like                    = ArrayField(models.IntegerField(null=True), null=True, size = 10000000)                                   #좋아요, 숫자는 최대

    def __str__(self):
        return self.MPID


class QnACommunity(models.Model):                                                                                           #QnA게시판
    QPID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    BID                     = models.ForeignKey("Book", on_delete=models.CASCADE ,null=True)                                #책 외래키
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    contents                = models.TextField(verbose_name='내용')                                                          #내용
    title                   = models.CharField(max_length=255, null=False)                                                   #제목
    postImage               = models.CharField(max_length=255, null=True)                                                   #여러개 어떻게?
    createAt                = models.DateField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateField(auto_now=True, null=False)                                                                   #수정날짜
    views                   = models.IntegerField(null=False, default = 0)                                                  #뷰
    like                    = ArrayField(models.IntegerField(null=True), null=True, size = 10000000)                                   #좋아요, 숫자는 최대
    parentQPID              = models.IntegerField(null=False, default = 0)                                                #답글 부모 QPID

    def __str__(self):
        return self.QPID


class HotCommunity(models.Model):                                                                                           #핫게시판
    HPID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    QPID                    = models.ForeignKey("QnACommunity", on_delete=models.CASCADE ,null=True)                        #유저 외래키
    APID                    = models.ForeignKey("AnyCommunity", on_delete=models.CASCADE ,null=True)                        #유저 외래키
    MPID                    = models.ForeignKey("MarketCommunity", on_delete=models.CASCADE ,null=True)                     #유저 외래키

    def __str__(self):
        return self.HPID


class AnyComment(models.Model):
    ACID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    APID                    = models.ForeignKey("AnyCommunity", on_delete=models.CASCADE ,null=False)                       #게시글 외래키
    parentID                = models.IntegerField(null=False, default = 0)                                                  #댓글ID
    comment                 = models.TextField(verbose_name='내용')                                                          #내용
    createAt                = models.DateField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateField(auto_now=True, null=False)                                                                   #수정날짜
    like                    = ArrayField(models.IntegerField(null=True), null=True, size = 10000000)                                   #좋아요, 숫자는 최대

    def __str__(self):
        return self.ACID


class QnAComment(models.Model):
    QCID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    QPID                    = models.ForeignKey("QnACommunity", on_delete=models.CASCADE ,null=False)                       #게시글 외래키
    parentID                = models.IntegerField(null=False, default = 0)                                                  #댓글ID
    comment                 = models.TextField(verbose_name='내용')                                                          #내용
    createAt                = models.DateField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateField(auto_now=True, null=False)                                                                   #수정날짜
    like                    = ArrayField(models.IntegerField(null=True), null=True, size = 10000000)                                   #좋아요, 숫자는 최대

    def __str__(self):
        return self.QCID


class MarketComment(models.Model):
    MCID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    MPID                    = models.ForeignKey("MarketCommunity", on_delete=models.CASCADE ,null=False)                    #게시글 외래키
    parentID                = models.IntegerField(null=False, default = 0)                                                  #댓글ID
    comment                 = models.TextField(verbose_name='내용')                                                          #내용
    createAt                = models.DateField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateField(auto_now=True, null=False)                                                                   #수정날짜
    like                    = ArrayField(models.IntegerField(null=True), null=True, size = 10000000)                                   #좋아요, 숫자는 최대

    def __str__(self):
        return self.MCID


class Review(models.Model):
    RID                     = models.BigAutoField(primary_key=True)                                                         #Primary Key
    BID                     = models.ForeignKey("Book", on_delete=models.CASCADE ,null=False)                               #책 외래키
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    contents                = models.TextField(verbose_name='내용')                                                          #내용
    views                   = models.IntegerField(null=False, default = 0)                                                  #뷰
    createAt                = models.DateField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateField(auto_now=True, null=False)                                                                   #수정날짜
    like                    = ArrayField(models.IntegerField(null=True), null=True, size = 10000000, default = list())                                   #좋아요, 숫자는 최대
    rating                  = models.FloatField(null=False, default=2.5)
    def __str__(self):
        return self.RID

class FavoriteBook(models.Model):
    FID                     = models.BigAutoField(primary_key=True)                                                         #Primary Key
    BID                     = models.ForeignKey("Book", on_delete=models.CASCADE ,null=False)                               #책 외래키
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키

    def __str__(self):
        return self.FID


class Notification(models.Model):
    NID                     = models.BigAutoField(primary_key=True)
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    contents                = models.CharField(max_length=50, null=True)                                                    #내용
    createAt                = models.DateField(auto_now_add=True, null=False)                                                   #생성날짜

    def __str__(self):
        return self.NID


class Tag(models.Model):
    TID                     = models.BigAutoField(primary_key=True)                                                         #Primary Key
    nameTag                 = models.CharField(max_length=255, null=False)                                                  #내용
    contents                = ArrayField(models.CharField(max_length=100, null=True), size = 10000000, null=True)                                   #좋아요, 숫자는 최대
    def __str__(self):
        return self.nameTag
    
class RefreshTokenStorage(models.Model) :
    RTID                    = models.BigAutoField(primary_key=True)
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)
    refresh_token           = models.CharField(max_length=255, null=False, blank=False)
    createAt                = models.DateField(auto_now=True)
    
    def __str__(self):
        return self.RTID

class AuthenticationCodeStorage(models.Model) :
    ATCID                   = models.BigAutoField(primary_key=True)
    email                   = models.EmailField(max_length=100, null=False)
    authCode_token          = models.CharField(max_length=255, null=False, blank=False)
    createAt                = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.email

class RecommendBook(models.Model):
    RBID                    = models.BigAutoField(primary_key=True)
    BID                     = ArrayField(models.IntegerField(null=False), size = 30, null=True)
    TID                     = models.ForeignKey("Tag", on_delete=models.CASCADE, null=False, default=150)
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE, null=False)
    
    def __str__(self):
        return self.RBID