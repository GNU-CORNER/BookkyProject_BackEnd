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
    print("[code_25_get_access] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(uid)+" Access토큰 발급") #로그 처리
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
        refreshData = {'UID' : uid, 'refresh_token':refresh_token} #UID, RefreshToken 페어로 저장
        authSerializer = RefreshTokenSerializer(data = refreshData) #RefreshToken 저장
        if authSerializer.is_valid():
            authSerializer.save()
            print("[code_47_get_refreshToken] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(uid)+" 갱신토큰 발급") #로그 처리
            return refresh_token
        else:
            print("[code_47_get_refreshToken] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(uid)+" 오류 : "+ authSerializer.errors)
            return 500
    else:
        return True
    
def re_generate_Token(access_token, refreshToken):
    secretKey = dbsetting.SECRET_KEY
    try:
        tempData = RefreshTokenStorage.objects.filter(refresh_token= refreshToken)
    except RefreshTokenStorage.DoesNotExist : #DB 연결 끊김
        return 5
    flag = valid_token(access_token)
    if flag == 2:
        if(len(tempData) != 0): #Valid 함수로 2차 확인 후 재생성
            try:
                user = jwt.decode(refreshToken, secretKey, algorithms=dbsetting.algorithm)
                if user['token_type'] == "refresh_token": #받은 토큰이 Refresh_Token 이 맞는지 확인
                    if(len(User.objects.filter(UID = tempData[0].UID.UID)) != 0): #해당 DB에 해당 UID가 존재하는지 확인
                        print("[code_64_re_generate_Token] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(tempData[0].UID.UID)+" 토큰 재발급") #로그 처리
                        new_access_token = get_access(tempData[0].UID.UID)
                        return new_access_token
            except jwt.ExpiredSignatureError: #JWT 갱신 토큰이 만료되었을 때
                print("[code_64_re_generate_Token] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(tempData[0].UID.UID)+" 갱신 토큰 만료")
                return 2
            except jwt.exceptions.DecodeError: #JWT 갱신 토큰의 형식 에러, 혹은 잘못된 토큰
                print("[code_64_re_generate_Token] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(tempData[0].UID.UID)+" 재발급 시도 중 오류")
                return 3
    elif flag == True: #Access Token의 유효기간이 남을때의 분기
        print("[code_64_re_generate_Token] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(tempData[0].UID.UID)+"유효기간 남음")
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
    return str(no_1)+str(no_2)+str(no_3)+str(no_4)+str(no_5)+str(no_6)+str(no_7)+str(no_8) #8개 각각 난수로 발급

def getAuthenticate(email):
    secretKey = dbsetting.SECRET_KEY
    tempData = AuthenticationCodeStorage.objects.filter(email = email) #발급할 이메일에 코드가 있는지 확인
    if len(tempData) != 0: #해당 이메일이 DB에 존재하면 삭제
        tempData.delete()
    temp = getCode() #코드 발급
    authCode_token = jwt.encode({'token_type':"authentication", 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=180), 'codeToken':temp}, secretKey, algorithm=dbsetting.algorithm).decode('utf-8') #만료시간 10분으로 지정
    authenticationData = {'email':email, 'authCode_token':authCode_token} #DB에 넣기 위한 정규화
    authSerializer = AuthenticationCodeTokenSerializer(data = authenticationData) 
    if authSerializer.is_valid(): #해당 이메일과 인코딩한 코드를 페어로 저장
        authSerializer.save()
    return temp

def checkAuthentication(inputEmail, code):
    try:
        data = AuthenticationCodeStorage.objects.filter(email = inputEmail) 
    except AuthenticationCodeStorage.DoesNotExist :
        return False
    if len(data) != 0 : #데이터 1차 확인 (DB에 있는지?) DB에서 코드를 발급한 이메일이 있는지 확인
        try:
            secretKey = dbsetting.SECRET_KEY
            authCode = jwt.decode(data[0].authCode_token, secretKey, algorithms=dbsetting.algorithm) 
            if str(code) == str(authCode['codeToken']) :#AuthCode 디코드 후 비교
                tempData = AuthenticationCodeStorage.objects.filter(email = inputEmail) 
                tempData.delete() #확인 후 성공시에 삭제
                return True
            else :
                return False        
        except jwt.DecodeError:
            return False
        except jwt.ExpiredSignatureError:
            return False
        