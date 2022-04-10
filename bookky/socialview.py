from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
import urllib3
from .models import User, RefreshTokenStorage
from .userserializers import UserRegisterSerializer
from .auth import setToken, get_access, get_refreshToken
#소셜 계정 확인
def socialEmailCheck(email):
    if len(User.objects.filter(email = email)) == 0:
        return True
    else:
        return False
    
#소셜 회원가입
@api_view(['POST'])
def socialSignup(request):
    try:
        data = JSONParser().parse(request)
    except User.DoesNotExist: #User 데이터베이스가 존재하지 않을 때, 혹은 DB와의 연결이 끊겼을 때 출력
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':"User에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"},status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        userData = User.objects
        #가입되지 않았으면
        if socialEmailCheck(data['email']):
            serializer = UserRegisterSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                temp = serializer.data
                del temp['pwToken']
                users = userData.get(email=data['email'])
                accessToken = get_access(users.UID)
                refreshToken = get_refreshToken(users.UID)
                if refreshToken :
                    tempData = RefreshTokenStorage.objects.filter(UID =users.UID)
                    refreshToken = tempData[0].refresh_token
                    return JsonResponse({"success" : True, "result": temp, 'errorMessage':"", 'access_token':str(accessToken), 'refresh_token' : str(refreshToken) }, status=status.HTTP_201_CREATED)
                elif refreshToken == 500:
                    return JsonResponse({'success':False, "result": {}, 'errorMessage':"serverError",'access_token':"", 'refresh_token' : ""}, status=status.HTTP_404_NOT_FOUND)
            else:
                return JsonResponse({'success' : False, "result": {}, 'errorMessage':"잘못된 형식의 데이터"}, status=status.HTTP_400_BAD_REQUEST)
        #가입되어 있으면
        else:
            JsonResponse({'success':False, 'result':{}, 'errorMessage':"이미 가입한 이메일입니다."}, status=status.HTTP_403_FORBIDDEN)

#소셜 로그인  
@api_view(['POST'])
def socialSignin(request):
    try:
        data = JSONParser().parse(request)
    except User.DoesNotExist: #User 데이터베이스가 존재하지 않을 때, 혹은 DB와의 연결이 끊겼을 때 출력
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':"User에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"},status=status.HTTP_404_NOT_FOUND)
    #로그인
    if (request.method == 'POST'):
        userData = User.objects
        if data['email'] is not None:
            #로그인
            if socialEmailCheck(data['email']) != True: #로그인 인증 인가를 통해서 생각 해봐야 할듯 
                users = userData.get(email=data['email'])
                if(users.pwToken == data['pwToken']): #로그인 성공
                    filteredData = userData.filter(email=data['email'])
                    serializer = UserRegisterSerializer(filteredData, many=True)
                    accessToken = get_access(users.UID)
                    refreshToken = get_refreshToken(users.UID)
                    if refreshToken :
                        tempData = RefreshTokenStorage.objects.filter(UID =users.UID)
                        refreshToken = tempData[0].refresh_token
                        temp = serializer.data[0]
                        del temp['pwToken']
                        return JsonResponse({"success" : True, "result": temp, 'errorMessage':"", 'access_token':str(accessToken), 'refresh_token' : str(refreshToken) }, status=status.HTTP_200_OK)
                    elif refreshToken == 500:
                        return JsonResponse({'success':False, "result": {}, 'errorMessage':"serverError",'access_token':"", 'refresh_token' : ""}, status=status.HTTP_404_NOT_FOUND)
                else: #로그인 비밀번호 틀림
                    return JsonResponse({"success" : False, "result": {}, 'errorMessage':"비밀번호가 틀렸습니다.",'access_token':"", 'refresh_token' : ""}, status=status.HTTP_400_BAD_REQUEST)
            else: #해당 이메일 정보 없음
                return JsonResponse({'success':False, 'result':{}, 'errorMessage':"해당하는 유저가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
            #회원가입 (성공 시 AT, RT를 넘겨 바로 로그인)
        else:
            return JsonResponse({'success' : False, "result": {}}, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
def social_github_login(request):
    if request.method == 'POST':
        data = JSONParser.parse(request)
        if data['redirect_URL'] is None or data['client_id'] is None or data['client_secret']:
            return JsonResponse({'success':False, 'result':{}, 'errorMessage':"redirect_URL이 없음"}, status = status.HTTP_400_BAD_REQUEST)
        else:
            userData = User.objects
            #회원가입

        