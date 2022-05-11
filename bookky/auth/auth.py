from datetime import datetime
import jwt
import bcrypt
import datetime
import random

from django.http import JsonResponse
from rest_framework import status
from bookky_backend import dbsetting
from bookky.models import User, RefreshTokenStorage, AuthenticationCodeStorage
from bookky.serializers.userserializers import RefreshTokenSerializer, AuthenticationCodeTokenSerializer

# 비밀번호 토큰 생성
def setToken(rawData): 
    hashed_pw = bcrypt.hashpw(rawData.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return hashed_pw

#비밀번호 대조
def checkToken(hashed_data, userData): 
    if bcrypt.checkpw(hashed_data.encode('utf-8'), userData.pwToken.encode('utf-8')):
        return True
    else:
        return False

#ACCESS_TOKEN 발급
def get_access(uid): 
    access_token = jwtEncoder(uid, 1)
    print("[code_25_get_access] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(uid)+" Access토큰 발급") #로그 처리
    return access_token

#ACCESS_TOKEN 만 확인 함
def valid_token(token): 
    try:
        user = jwtDecoder(token)
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

#RefreshToken 발급
def get_refreshToken(uid):
    tempData = RefreshTokenStorage.objects.filter(UID= uid)
    if len(tempData) == 0:
        refresh_token = jwtEncoder(None,2)
        authSerializer = RefreshTokenSerializer(data = {'UID' : uid, 'refresh_token':refresh_token}) #RefreshToken 저장 #UID, RefreshToken 페어로 저장
        if authSerializer.is_valid():
            authSerializer.save()
            print("[code_47_get_refreshToken] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(uid)+" 갱신토큰 발급") #로그 처리
            return refresh_token
        else:
            print("[code_47_get_refreshToken] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(uid)+" 오류 : "+ authSerializer.errors)
            return 500
    else:
        refresh_token = jwtEncoder(None,2)
        tempQuery = RefreshTokenStorage.objects.get(UID = uid)
        tempQuery.refresh_token = refresh_token
        tempQuery.save()
        print("[code_47_get_refreshToken] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(uid)+" 갱신토큰 발급") #로그 처리
        return refresh_token
    
#AT토큰 갱신
def re_generate_Token(request):
    try:
        tempData = RefreshTokenStorage.objects.filter(refresh_token= request.headers.get('refresh_token',None))
    except RefreshTokenStorage.DoesNotExist : #DB 연결 끊김
        return 5
    flag = valid_token(request.headers.get('access_token',None))
    if flag == 2:
        if(len(tempData) != 0): #Valid 함수로 2차 확인 후 재생성
            try:
                user = jwtDecoder(request.headers.get('refresh_token',None))
                if user['token_type'] == "refresh_token": #받은 토큰이 Refresh_Token 이 맞는지 확인
                    if(len(User.objects.filter(UID = tempData[0].UID.UID)) != 0): #해당 DB에 해당 UID가 존재하는지 확인
                        print("[code_64_re_generate_Token] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(tempData[0].UID.UID)+" 토큰 재발급") #로그 처리
                        new_access_token = get_access(tempData[0].UID.UID)
                        return new_access_token
                    else:
                        return 3
            except jwt.ExpiredSignatureError: #JWT 갱신 토큰이 만료되었을 때
                print("[code_64_re_generate_Token] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(tempData[0].UID.UID)+" 갱신 토큰 만료")
                return 2
            except jwt.exceptions.DecodeError: #JWT 갱신 토큰의 형식 에러, 혹은 잘못된 토큰
                print("[code_64_re_generate_Token] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(tempData[0].UID.UID)+" 재발급 시도 중 오류")
                return 3
        else:
            return 3
    elif flag == True: #Access Token의 유효기간이 남을때의 분기
        print("[code_64_re_generate_Token] 시간 : " + str(datetime.datetime.utcnow())+", UID : "+str(tempData[0].UID.UID)+"유효기간 남음")
        return 4
    else:
        return 3

#AT 확인 함수
def authValidation(request):
    if request.headers.get('access_token') is None:
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':"Authroization키가 없음"}, status=status.HTTP_401_UNAUTHORIZED) #JWT 토큰이 없을 때
    else:
        tempToken = request.headers.get('access_token',None)
        return valid_token(tempToken)

#인증코드 난수 생성기
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

#이메일 인증코드 보내는 함수
def getAuthenticate(email):
    tempData = AuthenticationCodeStorage.objects.filter(email = email) #발급할 이메일에 코드가 있는지 확인
    if len(tempData) != 0: #해당 이메일이 DB에 존재하면 삭제
        tempData.delete()
    temp = getCode() #코드 발급
    authCode_token = jwtEncoder(temp, 0)
    authenticationData = {'email':email, 'authCode_token':authCode_token} #DB에 넣기 위한 정규화
    authSerializer = AuthenticationCodeTokenSerializer(data = authenticationData) 
    if authSerializer.is_valid(): #해당 이메일과 인코딩한 코드를 페어로 저장
        authSerializer.save()
    return temp

#인증코드 확인 함수
def checkAuthentication(inputEmail, code):
    try:
        data = AuthenticationCodeStorage.objects.filter(email = inputEmail) 
    except AuthenticationCodeStorage.DoesNotExist :
        return False
    if len(data) != 0 : #데이터 1차 확인 (DB에 있는지?) DB에서 코드를 발급한 이메일이 있는지 확인
        try:
            authCode = jwtDecoder(data[0].authCode_token)
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

#AT확인, decode 함수
def checkAuth_decodeToken(request):
    if request.headers.get('access_token',None) is None :
        return 0 #Header에 AT가 없을 때
    else :
        try:
            data = jwtDecoder(request.headers.get('access_token',None))
            if data['token_type'] == "access_token":
                return data['UID']
        except jwt.DecodeError:
            return 1 #AT형식 에러
        except jwt.ExpiredSignatureError:
            return 2 #AT 유효기간 끝남
        
#JWT토큰 디코더
def jwtDecoder(token):
    secretKey = dbsetting.SECRET_KEY
    return jwt.decode(token, secretKey, algorithms=dbsetting.algorithm) 

#JWT토큰 인코더, 'Type' : 0 = Authentication, 1 = Authorication_ACCESS, 2 = Authorization_REFRESH
def jwtEncoder(data, type):
    tokenType = ""
    time = 0
    secretKey = dbsetting.SECRET_KEY
    if type == 0:
        tokenType = "Authentication"
        time = 180
        return jwt.encode({'token_type':tokenType, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=time), 'codeToken':data}, secretKey, algorithm=dbsetting.algorithm).decode('utf-8') #만료시간 10분으로 지정
    elif type == 1:
        tokenType = "access_token"
        time = 600
        return jwt.encode({'token_type':tokenType, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=time), 'UID':data}, secretKey, algorithm=dbsetting.algorithm).decode('utf-8') #만료시간 10분으로 지정
    elif type == 2:
        tokenType = "refresh_token"
        time = 1209600
        return jwt.encode({'token_type':tokenType, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=time)},secretKey,algorithm=dbsetting.algorithm).decode('utf-8') #갱신 토큰 기간 2주로 설정