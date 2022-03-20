from datetime import datetime
import jwt
import bcrypt
import datetime

from django.http import JsonResponse
from rest_framework import status
from bookky_backend import dbsetting
from .models import User

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
        if(len(User.objects.filter(UID = user['UID'])) != 0):
            return 1
        else :
            return 0
    except jwt.ExpiredSignatureError : #JWT 토큰의 만료시간이 지났을 경우
        return 2
    
    except jwt.exceptions.DecodeError: #JWT 토큰의 형식에러, 혹은 잘못된 토큰
        return 0

def get_refreshToken(uid):
    secretKey = dbsetting.SECRET_KEY
    refresh_token = jwt.encode({'token_type':"refresh_token", 'exp': datetime.datetime.utcnow() + datetime.timedelta(weeks=2), 'UID' : uid},secretKey,algorithm=dbsetting.algorithm).decode('utf-8') #갱신 토큰 기간 2주로 설정
    return refresh_token

def re_generate_Token(access_token, refresh_token):
    secretKey = dbsetting.SECRET_KEY
    if(valid_token(access_token) == 2): #Valid 함수로 2차 확인 후 재생성
        try:
            user = jwt.decode(refresh_token, secretKey, algorithms=dbsetting.algorithm)
            if user['token_type'] == "refresh_token":
                if(len(User.objects.filter(UID = user['UID'])) != 0):
                    new_access_token = get_access(user['UID'])
                    return new_access_token
        except jwt.ExpiredSignatureError: #JWT 갱신 토큰이 만료되었을 때
            return False
        except jwt.exceptions.DecodeError: #JWT 갱신 토큰의 형식 에러, 혹은 잘못된 토큰
            return False

def authValidation(request):
    if request.headers.get('Authorization') is None:
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':"Authroization키가 없음"}, status=status.HTTP_401_UNAUTHORIZED) #JWT 토큰이 없을 때
    else:
        if request.headers.get('RefreshToken',None) is not None: # AccessToken이 만료됬고, RefreshToken이 만료되지 않았을 때, AccessToken을 재발급 해주는 시나리오 
            refresh_access_token = re_generate_Token(request.headers.get('RefreshToken',None), request.headers.get('Authorization',None))
            return JsonResponse({'success':True, 'result': {}, 'errorMessage':"", 'access_token':str(refresh_access_token)}, status=status.HTTP_202_ACCEPTED) 
        else:
            tempToken = request.headers.get('Authorization',None)
            if valid_token(tempToken) == 0: #비정상 토큰
                return JsonResponse({'success':False, 'result': {}, 'errorMessage':"유효하지 않은 토큰입니다."}, status=status.HTTP_401_UNAUTHORIZED)
            elif valid_token(tempToken) == 1: #토큰 인증 완료
                return True
            elif valid_token(tempToken) == 2: #토큰 만료
                return JsonResponse({'success':False, 'result': {}, 'errorMessage':"기간이 지난 토큰입니다."}, status=status.HTTP_403_FORBIDDEN)
