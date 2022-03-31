from time import sleep
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from .models import User, RefreshTokenStorage
from .userserializers import UserRegisterSerializer
from .auth import setToken, get_access, checkToken, get_refreshToken, re_generate_Token, getAuthenticate, checkAuthentication, checkAuth_decodeToken
from django.core.mail import EmailMessage


#사용자 회원정보 업데이트, 회원탈퇴 API
@api_view(['GET','PUT', 'DELETE'])
def user(request):
    if request.headers.get('access_token') is None:
        return JsonResponse({'success':False, 'result':{}, 'errorMessage':"형식이 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        userID = checkAuth_decodeToken(request)
        if userID == 1:
            return JsonResponse({'success':False, 'result':{}, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_401_UNAUTHORIZED)
        elif userID == 2:
            return JsonResponse({'success':False, 'result':{}, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        else:                
            #회원정보 수정(닉네임, 썸네일)
            if (request.method == 'PUT'):
                data = JSONParser().parse(request)                  
                userData = User.objects
                if len(userData.filter(UID=userID)) == 0 :
                    return JsonResponse({'success':False,'result': {}}, safe=False, status=status.HTTP_204_NO_CONTENT)
                else:
                    print(data)
                    userData = userData.get(UID=userID)
                    data['email'] = userData.email
                    data['pwToken'] = userData.pwToken
                    temp = UserRegisterSerializer(userData, data=data)
                    if temp.is_valid():
                        temp.save()
                        temps = temp.data
                        del temps['pwToken']
                        return JsonResponse({'success':True,'result': temps, 'errorMessage':""}, safe=False, status=status.HTTP_200_OK)
                    else:
                        print(temp.errors)
            #회원탈퇴
            elif (request.method == 'DELETE'):
                userData = User.objects.filter(UID=userID)
                if len(userData) == 0 :
                    return JsonResponse({'success':False,'result': {}, 'errorMessage':"해당 이메일의 정보 없음"}, safe=False, status=status.HTTP_204_NO_CONTENT)
                else:
                    userData.delete()
                    return JsonResponse({'success':True, 'result':{}, 'errorMessage':""},status=status.HTTP_200_OK)

            #회원정보
            elif request.method == 'GET':
                user = User.objects
                if len(user.filter(UID = userID)) !=0 :
                    userData = user.get(UID = userID)
                    #Favorite테이블에서 해당 사용자의 UID를 기반으로 검색해서 데이터 셋 준비 (관심도서)
                    #각 Community테이블에서 사용자의 UID를 기반으로 검색해서 데이터 셋 준비 (내가쓴글)
                    #Review테이블에서 해당 사용자의 UID를 기반으로 검색해서 데이터 셋 준비 (내가 쓴 후기)
                    return JsonResponse({'success':True, 'result':{
                        'nickname' : userData.nickname,
                        'thumbnail' : "썸네일 담아서 주기",
                        'f_books' : [],#책 썸네일, 이름
                        'my_posts' :[], #커뮤니티 API가 나오면 양식에 맞추어 넣는다
                        'my_reviews':[] #사용자가 쓴 후기
                        #사용자의 데이터 전부 담는다
                        },'errorMessage':""}, status = status.HTTP_200_OK)
                else:
                    return JsonResponse({'success':False, 'result':{}, 'errorMessage':"해당하는 정보 없음"},status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def userSignIn(request):
    try:
        data = JSONParser().parse(request)
    except User.DoesNotExist: #User 데이터베이스가 존재하지 않을 때, 혹은 DB와의 연결이 끊겼을 때 출력
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':"User에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"},status=status.HTTP_404_NOT_FOUND)

    #로그인
    if (request.method == 'POST'):
        userData = User.objects
        if data['email'] is not None:
            #로그인
            if(len(userData.filter(email=data['email']))) != 0: #로그인 인증 인가를 통해서 생각 해봐야 할듯 
                users = userData.get(email=data['email'])
                if(checkToken(data['pwToken'], users)): #로그인 성공
                    filteredData = userData.filter(email=data['email'])
                    serializer = UserRegisterSerializer(filteredData, many=True)
                    accessToken = get_access(users.UID)
                    refreshToken = get_refreshToken(users.UID)
                    if refreshToken :
                        tempData = RefreshTokenStorage.objects.filter(UID =users.UID)
                        refreshToken = tempData[0].refresh_token
                        return JsonResponse({"success" : True, "result": serializer.data[0], 'errorMessage':"", 'access_token':str(accessToken), 'refresh_token' : str(refreshToken) }, status=status.HTTP_202_ACCEPTED)
                    elif refreshToken == 500:
                        return JsonResponse({'success':False, "result": {}, 'errorMessage':"serverError",'access_token':"", 'refresh_token' : ""}, status=status.HTTP_404_NOT_FOUND)
                    return JsonResponse({"success" : True, "result": serializer.data[0], 'errorMessage':"", 'access_token':str(accessToken), 'refresh_token' : str(refreshToken) }, status=status.HTTP_202_ACCEPTED)
                else: #로그인 비밀번호 틀림
                    return JsonResponse({"success" : False, "result": {}, 'errorMessage':"비밀번호가 틀렸습니다.",'access_token':"", 'refresh_token' : ""}, status=status.HTTP_400_BAD_REQUEST)
            else: #해당 이메일 정보 없음
                return JsonResponse({'success':False, 'result':{}, 'errorMessage':"해당하는 유저가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
            #회원가입 (성공 시 AT, RT를 넘겨 바로 로그인)
        else:
            return JsonResponse({'success' : False, "result": {}}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def userSignUp(request):
    try:
        data = JSONParser().parse(request)
    except User.DoesNotExist: #User 데이터베이스가 존재하지 않을 때, 혹은 DB와의 연결이 끊겼을 때 출력
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':"User에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"},status=status.HTTP_404_NOT_FOUND)

    #회원가입
    if (request.method == 'POST'):
        userData = User.objects
        if data['email'] is not None:
            #회원가입 (성공 시 AT, RT를 넘겨 바로 로그인)
            if(len(userData.filter(email=data['email']))) == 0: #회원가입 request에 넘어온 UID값과 DB안의 UID와 비교하여 존재하지 않으면, 회원가입으로 생각함
                data['pwToken'] = setToken(data['pwToken'])                          #토큰화 한 비밀번호를 넣는다
                userSerializer = UserRegisterSerializer(data = data)
                if userSerializer.is_valid():
                    userSerializer.save()
                    #동기 처리가 필요함 
                    users = userData.get(email=data['email'])
                    accessToken = get_access(users.UID)
                    refreshToken = get_refreshToken(users.UID)
                    if refreshToken :
                        tempData = RefreshTokenStorage.objects.filter(UID =users.UID)
                        refreshToken = tempData[0].refresh_token
                        return JsonResponse({"success" : True, "result": userSerializer.data, 'errorMessage':"", 'access_token':str(accessToken), 'refresh_token' : str(refreshToken) }, status=status.HTTP_201_CREATED)
                    elif refreshToken == 500:
                        return JsonResponse({'success':False, "result": {}, 'errorMessage':"serverError",'access_token':"", 'refresh_token' : ""}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return JsonResponse({'success' : False, "result": {}, 'errorMessage':"잘못된 형식의 데이터"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                JsonResponse({'success':False, 'result':{}, 'errorMessage':"해당 이메일 사용자가 존재함"},status = status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success' : False, "result": {}}, status=status.HTTP_400_BAD_REQUEST)
    
#중복확인 및 이메일 인증 코드 발급                     
@api_view(['POST'])
def checkEmail(request):
    data = JSONParser().parse(request)
    if(request.method == 'POST'):
        try:
            userData = User.objects.filter(email=data['email']) 
        except User.DoesNotExist:
            return JsonResponse({'success':False, 'result':{},'errorMessage':"DB연결이 끊겼거나 User 테이블이 존재하지 않음"}, status=status.HTTP_404_NOT_FOUND) #DB와 연결이 끊겼을 때
        if data['email'] is not None: #해당 이메일이 UserDB에 존재하는지 확인 (중복확인)
            if(len(userData.filter(email=data['email']))) != 0: #중복확인 불 통과
                return JsonResponse({'success':False, 'result':{}, 'errorMessage':"이미 존재하는 이메일입니다."}, status=status.HTTP_200_OK)
            else: #중복확인 통과
                temp = getAuthenticate(data['email'])
                email = EmailMessage('북키 서비스 인증 메일입니다.', str(temp), to=[str(data['email'])]) #인증코드 발송 코드 //Todo: 인증메일 양식 만들어야함
                email.send()
                return JsonResponse({'success':True, 'result':{'email' : data['email']}, 'errorMessage':""}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False, 'result':{}, 'errorMessage':"email 입력 값이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

#Code확인
@api_view(['POST'])
def checkCode(request):
    data = JSONParser().parse(request)
    if(request.method == 'POST'):
        if checkAuthentication(data['email'], data['code']): 
            return JsonResponse({'success':True, 'result':{},'errorMessage':""}, status=status.HTTP_202_ACCEPTED) #Code가 맞는경우
        else:
            return JsonResponse({'success':False, 'result':{},'errorMessage':"Code가 올바르지 않습니다."},status=status.HTTP_406_NOT_ACCEPTABLE) #Code가 틀렸을 경우
    
#AT토큰 갱신
@api_view(['POST'])
def refresh_token(request):
    # AccessToken이 만료됬고, RefreshToken이 만료되지 않았을 때, AccessToken을 재발급 해주는 시나리오 
    if request.method == 'POST':
        if request.headers.get('refresh_token',None) is not None: # request 헤더에 RefreshToken이라는 파라미터에 값이 실려 왔는가?
            refresh_access_token = re_generate_Token(request)
            if refresh_access_token == 2:
                return JsonResponse({'success':False, 'result': {}, 'errorMessage':"기간이 지난 토큰입니다.", 'access_token':{}}, status=status.HTTP_403_FORBIDDEN)  #RefreshToken의 기간이 지남
            elif refresh_access_token == 3:
                return JsonResponse({'success':False, 'result': {}, 'errorMessage':"유효하지 않은 토큰입니다.", 'access_token':{}}, status=status.HTTP_401_UNAUTHORIZED) #RefreshToken의 형식이 잘못됨
            elif refresh_access_token == 4:
                return JsonResponse({'success':False, 'result': {}, 'errorMessage':"유효한 토큰입니다.", 'access_token':{}}, status=status.HTTP_400_BAD_REQUEST) #AccessToken의 만료기간이 남음
            elif refresh_access_token == 5:
                return JsonResponse({'success':False, 'result': {}, 'errorMessage':"DB가 존재하지 않거나, 연결이 끊겼습니다.", 'access_token':{}}, status=status.HTTP_404_NOT_FOUND) #RefreshTokenStorage와의 연결이 끊김
            return JsonResponse({'success':True, 'result': {}, 'errorMessage':"", 'access_token':str(refresh_access_token)}, status=status.HTTP_202_ACCEPTED)
    else:
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':str(request.method) + " 호출은 지원하지 않습니다.", 'access_token':{}}, status=status.HTTP_403_FORBIDDEN) #POST가 아닌 방식으로 접근 했을 경우
    
#로그아웃
@api_view(['POST'])
def signOut(request):
    if request.method == "POST":
        if request.headers.get('access_token') is None:
            return JsonResponse({'success':False, 'result':{}, 'errorMessage':"형식이 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
             userID = checkAuth_decodeToken(request)
             if userID == 1:
                 return JsonResponse({'success':False, 'result':{}, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_401_UNAUTHORIZED)
             elif userID == 2:
                 return JsonResponse({'success':False, 'result':{}, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
             else: 
                tempQuery = RefreshTokenStorage.objects.get(UID = userID)
                tempQuery.delete()
                return JsonResponse({'success':True, 'result':{}, 'errorMessage':""}, status = status.HTTP_200_OK)

#관심분야 업데이트
@api_view(['PUT'])
def updateBoundary(request):
    if request.method == 'PUT':
        data = JSONParser.parse(request)
        user = User.objects
        if len(user.filter(email = data['email'])) != 0:
            userData = user.get(email = data['email'])
            userData.tag_array.append(data['tag_array'])
            userData.save()
            return JsonResponse({'success':True, 'result':userData, 'errorMessage':""},status = status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False, 'result':{},'errorMessage':"해당 정보 없음"},status = status.HTTP_400_BAD_REQUEST)