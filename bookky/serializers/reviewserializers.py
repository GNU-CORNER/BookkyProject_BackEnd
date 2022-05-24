from bookky.models import Review
from django.db.models import fields
from rest_framework import serializers

class ReviewPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['RID','TBID','UID','contents','views','createAt','updateAt','like', 'rating']

class ReviewGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['RID','TBID','UID','contents','views','createAt','like','rating']

'''

class Review(models.Model):
    RID                     = models.BigAutoField(primary_key=True)                                                         #Primary Key
    BID                     = models.ForeignKey("Book", on_delete=models.CASCADE ,null=False)                               #책 외래키
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE ,null=False)                               #유저 외래키
    contents                = models.TextField(verbose_name='내용')                                                          #내용
    views                   = models.IntegerField(null=False, default = 0)                                                  #뷰
    createAt                = models.DateField(auto_now_add=True, null=False)                                                   #생성날짜
    updateAt                = models.DateField(auto_now=True, null=False)                                                                   #수정날짜
    like                    = ArrayField(models.IntegerField(null=True), null=True, size = 10000000)                                   #좋아요, 숫자는 최대

    def __str__(self):
        return self.RID

'''