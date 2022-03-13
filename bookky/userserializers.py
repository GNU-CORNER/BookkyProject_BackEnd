from django.db.models import fields
from rest_framework import serializers
from .models import User

class UserRegisterSerializer(serializers.ModelSerializer): #최초 회원가입에서 사용될 Serializer
    class Meta:
        model = User
        fields = ['email', 'pwToken', 'nickname']

class UserUpdateSerializer(serializers.ModelSerializer): #사용자 업데이트에서 사용될 Serializer
    class Meta:
        model = User
        fields = ['email', 'nickname', 'thumbnail', 'tag_array', 'pushNoti', 'pushToken']
        
'''
    UID                     = models.BigAutoField(primary_key=True)                         #Primary Key
    email                   = models.EmailField(max_length=100, null=False)                 #이메일
    pwToekn                 = models.CharField(max_length=255, null=False)                  #이메일 인증 토큰 혹은 인증 Refresh Token값이 들어갈 것 같다.
    nickname                = models.CharField(max_length=10, null=False, default="북아무개") #닉네임 (기본값 '북아무개')
    thumbnail               = models.CharField(max_length=255, null=True)                   #프로필 이미지
    tag_array               = models.ArrayField(IntegerField(null=True), size=50)           #Tag Array 정수형 배열로 선언함 크기 50
    pushNoti                = models.BooleanField(null=False, default=False)                #푸쉬 알림 승인 값
    pushToken               = models.CharField(max_length=255, null=True)                   #푸쉬 토큰 저장용

'''