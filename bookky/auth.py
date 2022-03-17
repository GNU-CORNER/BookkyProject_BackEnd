import jwt
import bcrypt
from bookky_backend import dbsetting

def setToken(rawData): # 비밀번호 토큰 생성
    hashed_pw = bcrypt.hashpw(rawData.encode('uft-8'), bcrypt.gensalt()).decode('utf-8')
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