import jwt
import bcrypt

from django.http import JsonResponse
from rest_framework import status
from bookky_backend import dbsetting
from .models import User

def setToken(rawData): # 비밀번호 토큰 생성
    hashed_pw = bcrypt.hashpw(rawData.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return hashed_pw

def checkToken(hashed_data, userData): #비밀번호 대조
    if bcrypt.checkpw(hashed_data, userData.pwToken.encode('utf-8')):
        return True
    else:
        return False

def get_access(user): #ACCESS_TOKEN 발급
    secretKey = dbsetting.SECRET_KEY
    access_token = jwt.encode({'UID':user.UID}, secretKey, algorithm=dbsetting.algorithm)
    return access_token

def valid_token(token):
    try:
        user = jwt.decode(token, dbsetting, algorithm=dbsetting.algorithm)
        if(len(User.objects.filter(UID = user['UID'])) != 0):
            return True
        else :
            return False
    except jwt.exceptions.DecodeError:
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':"잘못된 토큰"}, status=status.HTTP_400_NOT_FOUND) 