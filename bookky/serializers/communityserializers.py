from django.db.models import fields
from rest_framework import serializers
from bookky.models import MarketCommunity, HotCommunity, QnACommunity, AnyCommunity, AnyComment, MarketComment, QnAComment

class AnyCommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnyCommunity
        fields = ['APID', 'title', 'contents', 'like']

class AnyCommunityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnyCommunity
        fields = ['title', 'contents', 'views', 'createAt','updateAt','like','UID']

class AnyCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnyComment
        fields = ['ACID', 'UID', 'APID', 'parentID', 'comment', 'updateAt', 'like']

class MarketCommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketCommunity
        fields = ['MPID', 'title', 'contents', 'like']

class MarketCommunityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketCommunity
        fields = ['title', 'contents', 'views', 'createAt','updateAt','like','UID']

class MarketCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnyComment
        fields = ['MCID', 'UID', 'MPID', 'parentID', 'comment', 'updateAt', 'like']

class QnACommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = QnACommunity
        fields = ['QPID', 'title', 'contents','parentQPID', 'like']

class QnACommunityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = QnACommunity
        fields = ['title', 'contents', 'views', 'createAt','updateAt','like','UID']

class QnACommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = QnAComment
        fields = ['QCID', 'UID', 'MPID', 'parentID', 'comment', 'updateAt', 'like']


class HotCommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = HotCommunity
        fields = ['HPID', 'ACID', 'MCID', 'QCID']

'''
class AnyCommunity(models.Model):                                                                                           #???????????????
    APID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    BID                     = models.ForeignKey("Book", on_delete=models.CASCADE ,null=True)                                #??? ?????????
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #?????? ?????????
    contents                = models.TextField(verbose_name='??????')                                                          #??????
    postImage               = models.CharField(max_length=255, null=True)                                                   #????????? ??????????
    createAt                = models.DateField(auto_now=True, null=False)                                                   #????????????
    updateAt                = models.DateField(null=True)                                                                   #????????????
    views                   = models.IntegerField(null=False, default = 0)                                                  #???
    like                    = ArrayField(models.IntegerField(null=True), size = 10000000)                                   #?????????, ????????? ??????

    def __str__(self):
        return self.APID


class MarketCommunity(models.Model):                                                                                        #??????????????? ????????? ??????
    MPID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    BID                     = models.ForeignKey("Book", on_delete=models.CASCADE ,null=True)                                #??? ?????????
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #?????? ?????????
    contents                = models.TextField(verbose_name='??????')                                                          #??????
    postImage               = models.CharField(max_length=255, null=True)                                                   #????????? ??????????
    createAt                = models.DateField(auto_now=True, null=False)                                                   #????????????
    updateAt                = models.DateField(null=True)                                                                   #????????????
    views                   = models.IntegerField(null=False, default = 0)                                                  #???
    like                    = ArrayField(models.IntegerField(null=True), size = 10000000)                                   #?????????, ????????? ??????

    def __str__(self):
        return self.MPID


class QnACommunity(models.Model):                                                                                           #QnA?????????
    QPID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    BID                     = models.ForeignKey("Book", on_delete=models.CASCADE ,null=True)                                #??? ?????????
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #?????? ?????????
    contents                = models.TextField(verbose_name='??????')                                                          #??????
    postImage               = models.CharField(max_length=255, null=True)                                                   #????????? ??????????
    createAt                = models.DateField(auto_now=True, null=False)                                                   #????????????
    updateAt                = models.DateField(null=True)                                                                   #????????????
    views                   = models.IntegerField(null=False, default = 0)                                                  #???
    like                    = ArrayField(models.IntegerField(null=True), size = 10000000)                                   #?????????, ????????? ??????

    def __str__(self):
        return self.QPID


class HotCommunity(models.Model):                                                                                           #????????????
    HPID                    = models.BigAutoField(primary_key=True)                                                         #Primary Key
    QPID                    = models.ForeignKey("QnACommunity", on_delete=models.CASCADE ,null=True)                        #?????? ?????????
    APID                    = models.ForeignKey("AnyCommunity", on_delete=models.CASCADE ,null=True)                        #?????? ?????????
    MPID                    = models.ForeignKey("MarketCommunity", on_delete=models.CASCADE ,null=True)                     #?????? ?????????

    def __str__(self):
        return self.HPID
'''