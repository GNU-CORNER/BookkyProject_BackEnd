from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from .models import User
from .userserializers import UserRegisterSerializer, UserUpdateSerializer
from .auth import setToken, get_access, checkToken, get_refreshToken, re_generate_Token, getAuthenticate, checkAuthentication
from django.core.mail import EmailMessage


#사용자 로그인, 회원가입, 회원정보 업데이트, 회원탈퇴 API
@api_view(['POST', 'PUT', 'DELETE'])
def userSign(request):                     
    try:
        data = JSONParser().parse(request)
    except User.DoesNotExist: #User 데이터베이스가 존재하지 않을 때, 혹은 DB와의 연결이 끊겼을 때 출력
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':"User에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"},status=status.HTTP_404_NOT_FOUND)

    #회원가입, 로그인
    if (request.method == 'POST'):
        userData = User.objects
        if data['email'] is not None:
            if(len(userData.filter(email=data['email']))) != 0: #로그인 인증 인가를 통해서 생각 해봐야 할듯 
                users = userData.get(email=data['email'])
                if(checkToken(data['pwToken'], users)): #로그인 성공
                    filteredData = userData.filter(email=data['email'])
                    serializer = UserRegisterSerializer(filteredData, many=True)
                    accessToken = get_access(users.UID)
                    refreshToken = get_refreshToken(users.UID)
                    return JsonResponse({"success" : True, "result": serializer.data[0], 'errorMessage':"", 'access_token':str(accessToken), 'refresh_token' : str(refreshToken) }, status=status.HTTP_202_ACCEPTED)
                else: #로그인 실패
                    return JsonResponse({"success" : False, "result": {}, 'errorMessage':"비밀번호가 틀렸습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            elif(len(userData.filter(email=data['email']))) == 0: #회원가입 request에 넘어온 UID값과 DB안의 UID와 비교하여 존재하지 않으면, 회원가입으로 생각함
                data['pwToken'] = setToken(data['pwToken'])                          #토큰화 한 비밀번호를 넣는다
                userSerializer = UserRegisterSerializer(data = data)
                if userSerializer.is_valid():
                    userSerializer.save()
                    return JsonResponse({'success': True, 'result':userSerializer.data,'errorMessage':""}, status = status.HTTP_201_CREATED)
            
                else:
                    return JsonResponse({'success' : False, "result": {}}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success' : False, "result": {}}, status=status.HTTP_400_BAD_REQUEST)

    #회원정보 업데이트
    elif (request.method == 'PUT'):
        userData = User.objects.filter(email=data['email'])
        if data['email'] is not None:
            if len(userData) == 0 :
                return JsonResponse({'success':False,'result': {}}, safe=False, status=status.HTTP_204_NO_CONTENT)
            else:
                filtTmp = UserUpdateSerializer(userData, many=True)
                userData = userData.get()
                serializer = UserUpdateSerializer(userData,data = data)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse({'success':True,'result': serializer.data}, safe=False, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({'success':False,'result': {}}, safe=False, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success':False, 'result':{}},status=status.HTTP_400_BAD_REQUEST)

    #회원탈퇴
    elif (request.method == 'DELETE'):
        userData = User.objects.filter(email=data['email'])
        if data['email'] is not None:
            if len(userData) == 0 :
                return JsonResponse({'success':False,'result': {}}, safe=False, status=status.HTTP_204_NO_CONTENT)
            else:
                filteredData = userData.filter(email=data['email'])
                filteredData.delete()
                return JsonResponse({'success':True, 'result':{}},status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False, 'result':{}},status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def checkEmail(request):#중복확인 API                     
    data = JSONParser().parse(request)
    if(request.method == 'POST'):
        try:
            userData = User.objects.filter(email=data['email'])
        except User.DoesNotExist:
            return JsonResponse({'success':False, 'result':{},'errorMessage':"DB연결이 끊겼거나 User 테이블이 존재하지 않음"}, status=status.HTTP_404_NOT_FOUND)
        if data['email'] is not None:
            if(len(userData.filter(email=data['email']))) != 0:
                return JsonResponse({'success':False, 'result':{}, 'errorMessage':"이미 존재하는 이메일입니다."}, status=status.HTTP_200_OK)
            else:
                temp = getAuthenticate(data['email'])
                email = EmailMessage('북키 서비스 인증 메일입니다.', str(temp), to=[data['email']])
                email.send()
                return JsonResponse({'success':True, 'result':{'email' : data['email']}, 'errorMessage':""}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False, 'result':{}, 'errorMessage':"email 입력 값이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def checkCode(request):
    data = JSONParser().parse(request)
    if(request.method == 'POST'):
        if checkAuthentication(data['email'], data['code']):
            return JsonResponse({'success':True, 'result':{},'errorMessage':""}, status=status.HTTP_202_ACCEPTED)
        else:
            return JsonResponse({'success':False, 'result':{},'errorMessage':"Code가 올바르지 않습니다."},status=status.HTTP_406_NOT_ACCEPTABLE)
    

@api_view(['POST'])
def refresh_token(request):
    if request.method == 'POST':
        if request.headers.get('RefreshToken',None) is not None: # AccessToken이 만료됬고, RefreshToken이 만료되지 않았을 때, AccessToken을 재발급 해주는 시나리오 
            refresh_access_token = re_generate_Token(request.headers.get('Authorization',None), request.headers.get('RefreshToken',None))
            print(refresh_access_token)
            if refresh_access_token == 2:
                return JsonResponse({'success':False, 'result': {}, 'errorMessage':"기간이 지난 토큰입니다.", 'access_token':{}}, status=status.HTTP_403_FORBIDDEN) 
            elif refresh_access_token == 3:
                return JsonResponse({'success':False, 'result': {}, 'errorMessage':"유효하지 않은 토큰입니다.", 'access_token':{}}, status=status.HTTP_401_FORBIDDEN)
            elif refresh_access_token == 4:
                return JsonResponse({'success':False, 'result': {}, 'errorMessage':"유효한 토큰입니다.", 'access_token':{}}, status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse({'success':True, 'result': {}, 'errorMessage':"", 'access_token':str(refresh_access_token)}, status=status.HTTP_202_ACCEPTED) 
    else:
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':str(request.method) + " 호출은 지원하지 않습니다.", 'access_token':{}}, status=status.HTTP_403_FORBIDDEN)