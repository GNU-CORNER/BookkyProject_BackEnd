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

def get_access(user): #ACCESS_TOKEN 발급
    secretKey = dbsetting.SECRET_KEY
    access_token = jwt.encode({'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=600), 'UID':user.UID}, secretKey, algorithm=dbsetting.algorithm).decode('utf-8')
    return access_token

def valid_token(token):
    try:
        secretKey = dbsetting.SECRET_KEY
        user = jwt.decode(token, secretKey,algorithm=dbsetting.algorithm)
        print(user)
        if(len(User.objects.filter(UID = user['UID'])) != 0):
            return True
        else :
            return False
    except jwt.ExpiredSignatureError :
        return False
    
    except jwt.exceptions.DecodeError:
        return False

def get_refreshToken():
    secretKey = dbsetting.SECRET_KEY
    refresh_token = jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(weeks=2)},secretKey,algorithm=dbsetting.algorithm).decode('utf-8')
    return refresh_token

def re_generate_Token(user, access_token, refresh_token):
    secretKey = dbsetting.SECRET_KEY
    if(valid_token(access_token) == False):
        try:
            jwt.decode(refresh_token, secretKey, algorithms=dbsetting.algorithm)
            new_access_token = get_access(user)
            return new_access_token
        except jwt.ExpiredSignatureError:
            return False
        except jwt.exceptions.DecodeError:
            return False
    