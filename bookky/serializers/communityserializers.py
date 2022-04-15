from django.db.models import fields
from rest_framework import serializers
from bookky.models import MarketCommunity, HotCommunity, QnACommunity, AnyCommunity, AnyComment, MarketComment, QnAComment

class AnyCommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnyCommunity
        fields = ['APID', 'title', 'contents']

class AnyCommunityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnyCommunity
        fields = ['title', 'contents', 'postImage', 'updateAt', 'views']

class AnyCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnyComment
        fields = ['ACID', 'parentID', 'comment', 'updateAt', 'like']

class MarketCommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketCommunity
        fields = ['MPID', 'BID', 'UID', 'title', 'contents', 'postImage', 'updateAt']
        
class QnACommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = QnACommunity
        fields = ['QPID', 'BID', 'UID', 'title', 'contents', 'postImage', 'updateAt']

class HotCommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = HotCommunity
        fields = ['HPID', 'ACID', 'MCID', 'QCID']

'''
class AnyCommunity(models.Model):                                                                                           #자유게시판
    APID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    BID                     = models.ForeignKey("Book", on_delete=models.CASCADE ,null=True)                                #책 외래키
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    contents                = models.TextField(verbose_name='내용')                                                          #내용
    postImage               = models.CharField(max_length=255, null=True)                                                   #여러개 어떻게?
    createAt                = models.DateField(auto_now=True, null=False)                                                   #생성날짜
    updateAt                = models.DateField(null=True)                                                                   #수정날짜
    views                   = models.IntegerField(null=False, default = 0)                                                  #뷰
    like                    = ArrayField(models.IntegerField(null=True), size = 10000000)                                   #좋아요, 숫자는 최대

    def __str__(self):
        return self.APID


class MarketCommunity(models.Model):                                                                                        #장터게시판 자게와 동일
    MPID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    BID                     = models.ForeignKey("Book", on_delete=models.CASCADE ,null=True)                                #책 외래키
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    contents                = models.TextField(verbose_name='내용')                                                          #내용
    postImage               = models.CharField(max_length=255, null=True)                                                   #여러개 어떻게?
    createAt                = models.DateField(auto_now=True, null=False)                                                   #생성날짜
    updateAt                = models.DateField(null=True)                                                                   #수정날짜
    views                   = models.IntegerField(null=False, default = 0)                                                  #뷰
    like                    = ArrayField(models.IntegerField(null=True), size = 10000000)                                   #좋아요, 숫자는 최대

    def __str__(self):
        return self.MPID


class QnACommunity(models.Model):                                                                                           #QnA게시판
    QPID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    BID                     = models.ForeignKey("Book", on_delete=models.CASCADE ,null=True)                                #책 외래키
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    contents                = models.TextField(verbose_name='내용')                                                          #내용
    postImage               = models.CharField(max_length=255, null=True)                                                   #여러개 어떻게?
    createAt                = models.DateField(auto_now=True, null=False)                                                   #생성날짜
    updateAt                = models.DateField(null=True)                                                                   #수정날짜
    views                   = models.IntegerField(null=False, default = 0)                                                  #뷰
    like                    = ArrayField(models.IntegerField(null=True), size = 10000000)                                   #좋아요, 숫자는 최대

    def __str__(self):
        return self.QPID


class HotCommunity(models.Model):                                                                                           #핫게시판
    HPID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    QPID                    = models.ForeignKey("QnACommunity", on_delete=models.CASCADE ,null=True)                        #유저 외래키
    APID                    = models.ForeignKey("AnyCommunity", on_delete=models.CASCADE ,null=True)                        #유저 외래키
    MPID                    = models.ForeignKey("MarketCommunity", on_delete=models.CASCADE ,null=True)                     #유저 외래키

    def __str__(self):
        return self.HPID
'''