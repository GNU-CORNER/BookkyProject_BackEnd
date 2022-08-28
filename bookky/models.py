import email
from email.policy import default
from django.contrib.postgres.fields import ArrayField
from django.db import models

def image_upload_path(instance, filename):
    return f'{instance.imageTitle}/{filename}'
def image_user_upload_path(instance, filename):
    return f'thumbnail/userThumbnail/{instance.email}/{filename}'
    
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
    imageTitle              = models.TextField(null=True)
    imageContent            = models.TextField(null=True)
    def __str__(self):
        return self.UID


class AnyCommunity(models.Model):                                                                                           #자유게시판
    APID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    TBID                    = models.ForeignKey("TempBook", on_delete=models.CASCADE ,null=True, blank=True)                                #책 외래키
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    contents                = models.TextField(verbose_name='내용')                                                          #내용
    title                   = models.CharField(max_length=255, null=False)                                                   #제목
    postImage               = ArrayField(models.TextField(null=True), size = 6, null=True, default = list(), blank=True)                                   # 이미지, 배열
    createAt                = models.DateTimeField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateTimeField(auto_now=True, null=False)                                                                   #수정날짜
    views                   = models.IntegerField(null=False, default = 0)                                                  #뷰
    like                    = ArrayField(models.IntegerField(null=True), null=True, size = 10000000, default = list())                                   #좋아요, 숫자는 최대

    def __str__(self):
        return self.APID


class MarketCommunity(models.Model):                                                                                        #장터게시판 자게와 동일
    MPID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    TBID                     = models.ForeignKey("TempBook", on_delete=models.CASCADE ,null=True, blank=True)                                #책 외래키
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    contents                = models.TextField(verbose_name='내용')                                                          #내용
    title                   = models.CharField(max_length=255, null=False)                                                   #제목
    postImage               = ArrayField(models.TextField(null=True), size = 6, null=True, default = list(), blank=True)                                   # 이미지, 배열
    createAt                = models.DateTimeField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateTimeField(auto_now=True, null=False)                                                                   #수정날짜
    views                   = models.IntegerField(null=False, default = 0)                                                  #뷰
    like                    = ArrayField(models.IntegerField(null=True), null=True, size = 10000000, default = list())                                   #좋아요, 숫자는 최대

    def __str__(self):
        return self.MPID


class QnACommunity(models.Model):                                                                                           #QnA게시판
    QPID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    TBID                     = models.ForeignKey("TempBook", on_delete=models.CASCADE ,null=True, blank=True)                                #책 외래키
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    contents                = models.TextField(verbose_name='내용')                                                          #내용
    title                   = models.CharField(max_length=255, null=False)                                                   #제목
    postImage               = ArrayField(models.TextField(null=True), size = 6, null=True, default = list(), blank=True)                                   # 이미지, 배열
    createAt                = models.DateTimeField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateTimeField(auto_now=True, null=False)                                                                   #수정날짜
    views                   = models.IntegerField(null=False, default = 0)                                                  #뷰
    like                    = ArrayField(models.IntegerField(null=True), null=True, size = 10000000, default = list())                                   #좋아요, 숫자는 최대
    parentQPID              = models.IntegerField(null=False)                                                #답글 부모 QPID

    def __str__(self):
        return self.QPID


class HotCommunity(models.Model):                                                                                           #핫게시판
    HPID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    QPID                    = models.ForeignKey("QnACommunity", on_delete=models.CASCADE ,null=True)                        #유저 외래키
    APID                    = models.ForeignKey("AnyCommunity", on_delete=models.CASCADE ,null=True)                        #유저 외래키
    MPID                    = models.ForeignKey("MarketCommunity", on_delete=models.CASCADE ,null=True)                     #유저 외래키
    createAt                = models.DateTimeField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateTimeField(auto_now=True, null=False)                                                   #수정날짜
    communityType           = models.IntegerField(null=False, default=0)
    def __str__(self):
        return self.HPID


class AnyComment(models.Model):
    ACID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    APID                    = models.ForeignKey("AnyCommunity", on_delete=models.CASCADE ,null=False)                       #게시글 외래키
    parentID                = models.IntegerField(null=False, default = 0)                                                  #댓글ID
    comment                 = models.TextField(verbose_name='내용')                                                          #내용
    createAt                = models.DateTimeField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateTimeField(auto_now=True, null=False)                                                                   #수정날짜
    like                    = ArrayField(models.IntegerField(null=True), null=False, size = 10000000, default = list())                                   #좋아요, 숫자는 최대

    def __str__(self):
        return self.ACID


class QnAComment(models.Model):
    QCID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    QPID                    = models.ForeignKey("QnACommunity", on_delete=models.CASCADE ,null=False)                       #게시글 외래키
    parentID                = models.IntegerField(null=False, default = 0)                                                  #댓글ID
    comment                 = models.TextField(verbose_name='내용')                                                          #내용
    createAt                = models.DateTimeField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateTimeField(auto_now=True, null=False)                                                                   #수정날짜
    like                    = ArrayField(models.IntegerField(null=True), null=False, size = 10000000, default = list())                                   #좋아요, 숫자는 최대

    def __str__(self):
        return self.QCID


class MarketComment(models.Model):
    MCID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    MPID                    = models.ForeignKey("MarketCommunity", on_delete=models.CASCADE ,null=False)                    #게시글 외래키
    parentID                = models.IntegerField(null=False, default = 0)                                                  #댓글ID
    comment                 = models.TextField(verbose_name='내용')                                                          #내용
    createAt                = models.DateTimeField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateTimeField(auto_now=True, null=False)                                                                   #수정날짜
    like                    = ArrayField(models.IntegerField(null=True), null=False, size = 10000000, default = list())                                   #좋아요, 숫자는 최대

    def __str__(self):
        return self.MCID


class Review(models.Model):
    RID                     = models.BigAutoField(primary_key=True)                                                         #Primary Key
    TBID                     = models.ForeignKey("TempBook", on_delete=models.CASCADE ,null=True)                               #책 외래키
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    contents                = models.TextField(verbose_name='내용')                                                          #내용
    views                   = models.IntegerField(null=False, default = 0)                                                  #뷰
    createAt                = models.DateTimeField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateTimeField(auto_now=True, null=False)                                                                   #수정날짜
    like                    = ArrayField(models.IntegerField(null=True), null=False, size = 10000000, default = list())                                   #좋아요, 숫자는 최대
    rating                  = models.FloatField(null=False, default=2.5)
    def __str__(self):
        return self.RID

class FavoriteBook(models.Model):
    FID                     = models.BigAutoField(primary_key=True)                                                         #Primary Key
    TBID                     = models.ForeignKey("TempBook", on_delete=models.CASCADE ,null=True)                               #책 외래키
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키

    def __str__(self):
        return self.FID


class Notification(models.Model):
    NID                     = models.BigAutoField(primary_key=True)
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    contents                = models.CharField(max_length=50, null=True)                                                    #내용
    createAt                = models.DateTimeField(auto_now_add=True, null=False)                                                   #생성날짜

    def __str__(self):
        return self.NID

    
class RefreshTokenStorage(models.Model) :
    RTID                    = models.BigAutoField(primary_key=True)
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)
    refresh_token           = models.CharField(max_length=255, null=False, blank=False)
    createAt                = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.RTID

class AuthenticationCodeStorage(models.Model) :
    ATCID                   = models.BigAutoField(primary_key=True)
    email                   = models.EmailField(max_length=100, null=False)
    authCode_token          = models.CharField(max_length=255, null=False, blank=False)
    createAt                = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

class RecommendBook(models.Model):
    RBID                    = models.BigAutoField(primary_key=True)
    TBID                     = ArrayField(models.IntegerField(null=False), size = 30, null=True)
    TMID                     = models.ForeignKey("TagModel", on_delete=models.CASCADE, null=False, default=150)
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE, null=False)
    
    def __str__(self):
        return self.RBID

class TagModel(models.Model):
    TMID                    = models.BigAutoField(primary_key=True)
    nameTag                 = models.CharField(max_length=255,null=False)
    searchName              = models.CharField(max_length=255, null=False, blank=False)

class TempBook(models.Model):
    TBID                     = models.BigAutoField(primary_key=True)                         #Primary Key
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
    TAG                     = ArrayField(models.IntegerField(null=True), size = 50, null=False,default=list())         #태그
    RATING                  = models.FloatField(null=False, default = 2.5)                  #별점 (기본값 2.5점)
    Allah_BID               = models.CharField(max_length=30, null=True)                    #알라딘 고유 책번호
    thumbnailImage          = models.CharField(max_length=255, null=True)
    searchName              = models.CharField(max_length=255, null=True, blank=False)
    
    def __str__(self):
        return self.TBID

class ReportingTable(models.Model):
    ReportId                = models.BigAutoField(primary_key=True)
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE, null=False)
    #커뮤니티 글을 외래키로 두어서 좋을게 무엇이 있을까? // 관리자 테이블에서 삭제하기 위해서? -> communityType과 PID가 있지만 각각의 케이스를 코드로 써야함 -> 불필요 그냥 테이블에 컬럼을 추가하는게 추가적인 코드가 덜 필요하다.
    QPID                    = models.ForeignKey("QnACommunity", on_delete=models.CASCADE ,null=True)                        
    APID                    = models.ForeignKey("AnyCommunity", on_delete=models.CASCADE ,null=True)                        
    MPID                    = models.ForeignKey("MarketCommunity", on_delete=models.CASCADE ,null=True)                     #게시판 외래키
    QCID                    = models.ForeignKey("QnAComment", on_delete=models.CASCADE ,null=True)                        
    ACID                    = models.ForeignKey("AnyComment", on_delete=models.CASCADE ,null=True)                        
    MCID                    = models.ForeignKey("MarketComment", on_delete=models.CASCADE ,null=True)                     #게시판 외래키
    TYPE                    = models.IntegerField(null=False)
    reportType              = models.IntegerField(null=False)                                                               #리포트 종류
    createAt                = models.DateTimeField(auto_now_add=True, null=False)                                                   #생성날짜
    #커뮤니티 글을 자동 삭제는 쉽지만 엉뚱한 글 삭제가 일어날 수 있다. -> 즉, 수동으로 관리해야 한다. -> 관리자가 계속해서 검토해야 한다. -> 관리자 페이지를 작성해야 한다. 으악.

    def __str__(self):
        return self.ReportId 

class SuperUser(models.Model):
    SUID                    = models.BigAutoField(primary_key=True)
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE, null=False)
    authority               = models.IntegerField(null=False, default = 5)   # 1:최상위 권한, 2:관리자, 5: 일반 사용자
    def __str__(self):
        if self.authority == 1:
            return "Master"
        elif self.authority ==2 :
            return "Manager"
        elif self.authority ==5 :
            return "Common"
class BlackList(models.Model):
    BLACKID                 = models.BigAutoField(primary_key=True)
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE, null=False)
    createAt                = models.DateTimeField(auto_now_add=True, null=False)
    releaseAt               = models.DateTimeField(auto_now_add=True, null=False)
    ReportId                = models.ForeignKey("ReportingTable", on_delete=models.CASCADE, null=False)
    def __str__(self):
        return self.BLACKID
