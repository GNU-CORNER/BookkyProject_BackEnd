from datetime import datetime
import re
import jwt
import bcrypt
import datetime
import random

from django.http import JsonResponse
from rest_framework import status
from bookky_backend import dbsetting
from .models import User, RefreshTokenStorage, AuthenticationCodeStorage
from .userserializers import RefreshTokenSerializer, AuthenticationCodeTokenSerializer


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
        if user['token_type'] == "access_token":
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
    tempData = RefreshTokenStorage.objects.filter(UID= uid)
    if len(tempData) == 0:
        refresh_token = jwt.encode({'token_type':"refresh_token", 'exp': datetime.datetime.utcnow() + datetime.timedelta(weeks=2)},secretKey,algorithm=dbsetting.algorithm).decode('utf-8') #갱신 토큰 기간 2주로 설정
        refreshData = {'UID' : uid, 'refresh_token':refresh_token}
        authSerializer = RefreshTokenSerializer(data = refreshData) #RefreshToken 저장

        if authSerializer.is_valid():
            authSerializer.save()
            return refresh_token
        else:
            print(authSerializer.errors)
            return 500
    else:
        return True
    
def re_generate_Token(access_token, refreshToken):
    secretKey = dbsetting.SECRET_KEY
    try:
        tempData = RefreshTokenStorage.objects.filter(refresh_token= refreshToken)
    except RefreshTokenStorage.DoesNotExist :
        return 5
    if valid_token(access_token) == 2:
        if(len(tempData) != 0): #Valid 함수로 2차 확인 후 재생성
            try:
                user = jwt.decode(refreshToken, secretKey, algorithms=dbsetting.algorithm)
                if user['token_type'] == "refresh_token":
                    if(len(User.objects.filter(UID = tempData[0].UID.UID)) != 0):
                        new_access_token = get_access(tempData[0].UID.UID)
                        return new_access_token
            except jwt.ExpiredSignatureError: #JWT 갱신 토큰이 만료되었을 때
                return 2
            except jwt.exceptions.DecodeError: #JWT 갱신 토큰의 형식 에러, 혹은 잘못된 토큰
                print("asd")
                return 3
        else:
            print("ggg")
            return 4
    else:
        return 3


def authValidation(request):
    if request.headers.get('Authorization') is None:
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':"Authroization키가 없음"}, status=status.HTTP_401_UNAUTHORIZED) #JWT 토큰이 없을 때
    else:
        tempToken = request.headers.get('Authorization',None)
        return valid_token(tempToken)

def getCode():
    no_1 = random.randrange(1, 10)
    no_2 = random.randrange(0, 10)
    no_3 = random.randrange(0, 10)
    no_4 = random.randrange(0, 10)
    no_5 = random.randrange(0, 10)
    no_6 = random.randrange(0, 10)
    no_7 = random.randrange(0, 10)
    no_8 = random.randrange(0, 10)
    return str(no_1)+str(no_2)+str(no_3)+str(no_4)+str(no_5)+str(no_6)+str(no_7)+str(no_8)

def getAuthenticate(email):
    secretKey = dbsetting.SECRET_KEY
    temp = getCode()
    authCode_token = jwt.encode({'token_type':"authentication", 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=180), 'codeToken':temp}, secretKey, algorithm=dbsetting.algorithm).decode('utf-8') #만료시간 10분으로 지정
    authenticationData = {'email':email, 'authCode_token':authCode_token}
    authSerializer = AuthenticationCodeTokenSerializer(data = authenticationData)
    if authSerializer.is_valid():
        authSerializer.save()
    return temp

def checkAuthentication(inputEmail, code):
    try:
        data = AuthenticationCodeStorage.objects.get(email = inputEmail)
    except AuthenticationCodeStorage.DoesNotExist :
        return False
    if len(data) != 0 : #데이터 1차 확인 (DB에 있는지?)
        try:
            secretKey = dbsetting.SECRET_KEY
            authCode = jwt.decode(data[0].authCode_token, secretKey, algorithms=dbsetting.algorithm)
            if str(code) == str(authCode['codeToken']) :
                tempData = AuthenticationCodeStorage.objects.filter(email = inputEmail)
                tempData.delete()
                return True
            else :
                return False        
        except jwt.DecodeError:
            return False
        except jwt.ExpiredSignatureError:
            return False
        