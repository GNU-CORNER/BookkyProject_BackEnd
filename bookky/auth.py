from datetime import datetime
import jwt
import bcrypt
import datetime

from django.http import JsonResponse
from rest_framework import status
from bookky_backend import dbsetting
from .models import User, RefreshTokenStorage
from .userserializers import RefreshTokenSerializer


def setToken(rawData): # 비밀번호 토큰 생성
    hashed_pw = bcrypt.hashpw(rawData.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return hashed_pw

def checkToken(hashed_data, userData): #비밀번호 대조
    if bcrypt.checkpw(hashed_data.encode('utf-8'), userData.pwToken.encode('utf-8')):
        return True
    else:
        return False

def get_access(uid): #ACCESS_TOKEN 발급
    secretKey = dbsetting.SECRET_KEY
    access_token = jwt.encode({'token_type':"access_token", 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=600), 'UID':uid}, secretKey, algorithm=dbsetting.algorithm).decode('utf-8') #만료시간 10분으로 지정
    return access_token

def valid_token(token): #ACCESS_TOKEN 만 확인 함
    try:
        secretKey = dbsetting.SECRET_KEY
        user = jwt.decode(token, secretKey,algorithm=dbsetting.algorithm)
        print(user)
        if user['token_type'] == "access_token":
            print(user)
            if(len(User.objects.filter(UID = user['UID'])) != 0):
                return True
            else :
                return 0
        else :
            return 0
    except jwt.ExpiredSignatureError : #JWT 토큰의 만료시간이 지났을 경우
        return 2
    
    except jwt.exceptions.DecodeError: #JWT 토큰의 형식에러, 혹은 잘못된 토큰
        return 0

def get_refreshToken(uid):
    secretKey = dbsetting.SECRET_KEY
    refresh_token = jwt.encode({'token_type':"refresh_token", 'exp': datetime.datetime.utcnow() + datetime.timedelta(weeks=2), 'UID' : uid},secretKey,algorithm=dbsetting.algorithm).decode('utf-8') #갱신 토큰 기간 2주로 설정
    refreshData = {'UID' : uid, 'refresh_token':refresh_token}
    authSerializer = RefreshTokenSerializer(data = refreshData) #RefreshToken 저장
    if authSerializer.is_valid():
        authSerializer.save()
        return refresh_token
    else:
        print(authSerializer.errors)
    
def re_generate_Token(access_token, refreshToken):
    secretKey = dbsetting.SECRET_KEY
    try:
        tempData = RefreshTokenStorage.objects.filter(refresh_token= refreshToken)
    except RefreshTokenStorage.DoesNotExist :
        return 5
    if valid_token(access_token) == 2:
        if(tempData[0] != 0): #Valid 함수로 2차 확인 후 재생성
            try:
                user = jwt.decode(refreshToken, secretKey, algorithms=dbsetting.algorithm)
                if user['token_type'] == "refresh_token":
                    if(len(User.objects.filter(UID = tempData['UID'])) != 0):
                        new_access_token = get_access(tempData['UID'])
                        print(new_access_token)
                        return new_access_token
            except jwt.ExpiredSignatureError: #JWT 갱신 토큰이 만료되었을 때
                return 2
            except jwt.exceptions.DecodeError: #JWT 갱신 토큰의 형식 에러, 혹은 잘못된 토큰
                return 3
        else:
            return 4
    else:
        return 3


def authValidation(request):
    if request.headers.get('Authorization') is None:
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':"Authroization키가 없음"}, status=status.HTTP_401_UNAUTHORIZED) #JWT 토큰이 없을 때
    else:
        tempToken = request.headers.get('Authorization',None)
        return valid_token(tempToken)


                
