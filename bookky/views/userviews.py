from time import sleep
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from bookky.models import User, RefreshTokenStorage, TagModel
from bookky.serializers.userserializers import UserRegisterSerializer
from bookky.auth.auth import setToken, get_access, checkToken, get_refreshToken, re_generate_Token, getAuthenticate, checkAuthentication, checkAuth_decodeToken
from django.core.mail import send_mail
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg import openapi
from django.template.loader import render_to_string
from sendgrid.helpers.mail import *
from sendgrid import *
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
import bookky_backend.emailsetting as emailsetting
import os 

def emailCheck(email):
    if len(User.objects.filter(email = email)) == 0:
        return True
    else:
        return False


@swagger_auto_schema(
    method='delete',
    operation_description="회원탈퇴",
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={

                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)

#사용자 회원정보 업데이트, 회원탈퇴 API
@api_view(['DELETE'])
def user(request):
    # exceptDict = {"UID": 0,"email": "","nickname": "","pushToken": "","pushNoti": False,"thumbnail": "", "loginMethod": 0, "tag_array": []}
    exceptDict = None
    """
```json
    User 관련 API
```
    """
    if request.headers.get('access_token') is None:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"형식이 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        userID = checkAuth_decodeToken(request)
        if userID == -1:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        elif userID == -2:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_401_UNAUTHORIZED)
        else:                
            #회원정보 수정(닉네임, 썸네일)
            if (request.method == 'PUT'):
                data = JSONParser().parse(request)                  
                userData = User.objects
                if len(userData.filter(UID=userID)) == 0 :
                    return JsonResponse({'success':False,'result': exceptDict}, safe=False, status=status.HTTP_400_BAD_REQUEST)
                else:
                    userData = userData.get(UID=userID)
                    data['email'] = userData.email
                    data['pwToken'] = userData.pwToken
                    temp = UserRegisterSerializer(userData, data=data)
                    if temp.is_valid():
                        temp.save()
                        temps = temp.data
                        del temps['pwToken']
                        return JsonResponse({'success':True,'result': {'userData' :temps}, 'errorMessage':""}, safe=False, status=status.HTTP_200_OK)
                    else:
                        print(temp.errors)
                        return JsonResponse({'success':False,'result':exceptDict, 'errorMessage':"서버 에러"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            #회원탈퇴
            elif (request.method == 'DELETE'):
                userData = User.objects.filter(UID=userID)
                if len(userData) == 0 :
                    return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"해당 이메일의 정보 없음"}, safe=False, status=status.HTTP_204_NO_CONTENT)
                else:
                    userData.delete()
                    return JsonResponse({'success':True, 'result':exceptDict, 'errorMessage':""},status=status.HTTP_200_OK)

            #회원정보
            elif request.method == 'GET':
                # exceptDict = {'nickname' : "", 'thumbnail' : "", 'f_books' : [], 'my_posts' :[], 'my_reviews':[]}
                exceptDict = None
                user = User.objects
                if len(user.filter(UID = userID)) !=0 :
                    userData = user.get(UID = userID)
                    #Favorite테이블에서 해당 사용자의 UID를 기반으로 검색해서 데이터 셋 준비 (관심도서)
                    #각 Community테이블에서 사용자의 UID를 기반으로 검색해서 데이터 셋 준비 (내가쓴글)
                    #Review테이블에서 해당 사용자의 UID를 기반으로 검색해서 데이터 셋 준비 (내가 쓴 후기)
                    return JsonResponse({'success':True, 'result':{'userData':{
                        'nickname' : userData.nickname,
                        'thumbnail' : "썸네일 담아서 주기",
                        'f_books' : [],#책 썸네일, 이름
                        'my_posts' :[], #커뮤니티 API가 나오면 양식에 맞추어 넣는다
                        'my_reviews':[] #사용자가 쓴 후기
                        #사용자의 데이터 전부 담는다
                        }},'errorMessage':""}, status = status.HTTP_200_OK)
                else:
                    return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"해당하는 정보 없음"},status = status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',  
    request_body=openapi.Schema(
        '해당 내용의 titile',
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema('사용자 email ID', type=openapi.TYPE_STRING),
            'pwToken': openapi.Schema('사용자 비밀번호', type=openapi.TYPE_STRING),
            'loginMethod' : openapi.Schema('로그인 방식', type=openapi.TYPE_INTEGER)
        },
        required=['email', 'pwToken']  # 필수값을 지정 할 Schema를 입력해주면 된다.
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'userData' : openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'email' : openapi.Schema('사용자 email ID', type=openapi.TYPE_STRING),
                                'nickname' : openapi.Schema('사용자 닉네임', type=openapi.TYPE_STRING),
                                'pushToken' : openapi.Schema('사용자 pushToken', type=openapi.TYPE_STRING),
                                'pushNoti' : openapi.Schema('사용자 push알림 여부', type=openapi.TYPE_BOOLEAN),
                                'thumbnail' : openapi.Schema('사용자 썸네일', type=openapi.TYPE_STRING),
                                'loginMethod' : openapi.Schema('사용자 회원가입 방식', type=openapi.TYPE_INTEGER)
                            }
                        ),
                        'access_token' : openapi.Schema('AccessToken', type=openapi.TYPE_STRING),
                        'refresh_token' : openapi.Schema('RefreshToken', type=openapi.TYPE_STRING)
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING),
            }
        )
    }
)
@api_view(['POST'])
def userSignIn(request):
    # exceptDict = { "email" : "", "nickname" : "", "pushToken" : "", "pushNoti" : "", "thumbnail" : "", "loginMethod" : 0}
    exceptDict = None
    """

    로그인

    - slug : 0 = 자체 회원가입, 1 = Github, 2 = Google, 3 = Apple

    # Body
    ```json
    {
    	"email" : String,  //사용자 이메일
    	"pwToken" : String,	//사용자 비밀번호 (서버에서 알아서 인코딩 되니깐 RAW데이터로 보내도 됨)
        "loginMethod" : Integer
    }
    ```

    # Response
    ```json
    {
      	"success": Boolean,
    		"result" : {
                "userData":{
                    "email" : String,
    			    "nickname" : String,
    			    "pushToken" : String,
    			    "pushNoti" : Boolean,
                    "loginMethod" : Integer,
                    "thumbnail" : String,
                },
                "access_token" : String,
    	        "refresh_token" : String
    		},
    	"errorMessage": String,
    }
    ```

    """
    try:
        data = JSONParser().parse(request)
    except User.DoesNotExist: #User 데이터베이스가 존재하지 않을 때, 혹은 DB와의 연결이 끊겼을 때 출력
        return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"User에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"},status=status.HTTP_404_NOT_FOUND)

    #로그인
    if (request.method == 'POST'):
        userData = User.objects
        if data['email'] is not None:
            #로그인
            if len(userData.filter(email = data['email'])) != 0: #로그인 인증 인가를 통해서 생각 해봐야 할듯 
                users = userData.get(email=data['email'])
                if data['loginMethod'] is not None:
                    if(checkToken(data['pwToken'], users)): #로그인 성공
                        filteredData = userData.filter(email=data['email'])
                        serializer = UserRegisterSerializer(filteredData, many=True)
                        accessToken = get_access(users.UID)
                        refreshToken = get_refreshToken(users.UID)
                        temp = serializer.data[0]
                        del temp['pwToken']
                        if temp['tag_array'] is not None:
                            tempTag = []
                            tagQuery = TagModel.objects
                            for i in temp['tag_array']:
                                temps = tagQuery.get(TMID = i)                                
                                tempTag.append(temps.nameTag)
                            temp['tag_array'] = tempTag
                        return JsonResponse({"success" : True, "result": {'userData':temp, 'access_token':str(accessToken), 'refresh_token' : str(refreshToken)}, 'errorMessage':""}, status=status.HTTP_200_OK)
                        if refreshToken == 500:
                            return JsonResponse({'success':False, "result": exceptDict, 'errorMessage':"serverError"}, status=status.HTTP_404_NOT_FOUND)
                    else: #로그인 비밀번호 틀림
                        return JsonResponse({"success" : False, "result": exceptDict, 'errorMessage':"비밀번호가 틀렸습니다."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"LoginMethod가 없습니다.."},status=status.HTTP_400_BAD_REQUEST)
            else: #해당 이메일 정보 없음
                return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"해당하는 유저가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
                #Github 로그인
        else:
            return JsonResponse({'success' : False, "result": exceptDict,'errorMessage':"email정보가 없음"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',  
    request_body=openapi.Schema(
        '해당 내용의 titile',
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema('사용자 email ID', type=openapi.TYPE_STRING),
            'nickname':openapi.Schema('사용자 닉네임', type=openapi.TYPE_STRING),
            'pwToken': openapi.Schema('사용자 비밀번호', type=openapi.TYPE_STRING),
            'loginMethod' : openapi.Schema('로그인 방식', type=openapi.TYPE_INTEGER)
        },
        required=['email', 'nickname', 'pwToken']  # 필수값을 지정 할 Schema를 입력해주면 된다.
    ),
    responses={
        201: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'userData' : openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'email' : openapi.Schema('사용자 email ID', type=openapi.TYPE_STRING),
                                'nickname' : openapi.Schema('사용자 닉네임', type=openapi.TYPE_STRING),
                                'pushToken' : openapi.Schema('사용자 pushToken', type=openapi.TYPE_STRING),
                                'pushNoti' : openapi.Schema('사용자 push알림 여부', type=openapi.TYPE_BOOLEAN),
                                'thumbnail' : openapi.Schema('사용자 썸네일', type=openapi.TYPE_STRING),
                                'loginMethod' : openapi.Schema('사용자 회원가입 방식', type=openapi.TYPE_INTEGER)
                            }
                        ),
                        'access_token' : openapi.Schema('AccessToken', type=openapi.TYPE_STRING),
                        'refresh_token' : openapi.Schema('RefreshToken', type=openapi.TYPE_STRING)
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING),
            }
        )
    }
)
@api_view(['POST'])
def userSignUp(request):
    # exceptDict = { "email" : "", "nickname" : "", "pushToken" : "", "pushNoti" : False, "thumbnail" : "", "loginMethod" : 0}
    exceptDict = None
    """

    회원가입

    - slug : 0 = 자체 회원가입, 1 = Github, 2 = Google, 3 = Apple

# Body
```json
{
	"email" : String,  //사용자 이메일
	"nickname" : String, //사용자 닉네임
	"pwToken" : String,	//사용자 비밀번호 (서버에서 알아서 인코딩 되니깐 RAW데이터로 보내도 됨)
    "loginMethod" : Integer
}
```

# Response
```json
{
	"success": Boolean,
    "result" : {
        "userData":{
            "email" : String,
    		"nickname" : String,
    		"pushToken" : String,
    		"pushNoti" : Boolean,
            "loginMethod" : Integer,
            "thumbnail" : String,
            },
            "access_token" : String,
    	    "refresh_token" : String
    	},
    "errorMessage": String,
}
```
    """
    try:
        data = JSONParser().parse(request)
    except User.DoesNotExist: #User 데이터베이스가 존재하지 않을 때, 혹은 DB와의 연결이 끊겼을 때 출력
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':"User에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"},status=status.HTTP_404_NOT_FOUND)

    #회원가입
    if (request.method == 'POST'):
        userData = User.objects
        if data['email'] is not None and data['nickname'] is not None:
            #회원가입 (성공 시 AT, RT를 넘겨 바로 로그인)
            if len(userData.filter(email = data['email'])) == 0 : #회원가입 request에 넘어온 UID값과 DB안의 UID와 비교하여 존재하지 않으면, 회원가입으로 생각함
                if data['loginMethod'] is not None :
                    data['pwToken'] = setToken(data['pwToken'])                          #토큰화 한 비밀번호를 넣는다
                    userSerializer = UserRegisterSerializer(data = data)
                    if userSerializer.is_valid():
                        userSerializer.save()
                        temp = userSerializer.data
                        del temp['pwToken']
                        #동기 처리가 필요함 
                        users = userData.get(email=data['email'])
                        accessToken = get_access(users.UID)
                        refreshToken = get_refreshToken(users.UID)
                        if refreshToken :
                            tempData = RefreshTokenStorage.objects.filter(UID =users.UID)
                            refreshToken = tempData[0].refresh_token
                            return JsonResponse({"success" : True, "result": {'userData':temp, 'access_token':str(accessToken), 'refresh_token' : str(refreshToken)}, 'errorMessage':""}, status=status.HTTP_201_CREATED)
                        elif refreshToken == 500:
                            return JsonResponse({'success':False, "result": exceptDict, 'errorMessage':"serverError"}, status=status.HTTP_404_NOT_FOUND)
                        else:
                            return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':""}, status = status.HTTP_400_BAD_REQUEST)
                    else:
                        print(userSerializer.errors)
                        return JsonResponse({'success' : False, "result": exceptDict, 'errorMessage':"잘못된 형식의 데이터"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return JsonResponse({'success' : False, "result": exceptDict, 'errorMessage':"LoginMethod가 없음"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'success':False,'result':exceptDict, 'errorMessage':""},status = status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success' : False, "result": exceptDict, 'errorMessage':""}, status=status.HTTP_400_BAD_REQUEST)
    

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('email',openapi.IN_QUERY,type=openapi.TYPE_STRING, description='이메일')
    ],

    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'email' : openapi.Schema('사용자 email ID', type=openapi.TYPE_STRING),
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING),
            }
        )
    }
)
#중복확인 및 이메일 인증 코드 발급                     
@api_view(['GET'])
def checkEmail(request):
    """
    이메일 인증코드 발급 & 중복확인

    - 인증코드 만료시간 3분임

# Response
```json
{
    "success": Boolean, //False 이면 중복
    "result": {
        "email": String
    },
    "errorMessage": String
}
```

    """
    
    if(request.method == 'GET'):
        # exceptDict = {'email':""}
        exceptDict = None
        try:
            data = request.GET.get('email')
            userData = User.objects.filter(email=data) 
        except User.DoesNotExist:
            return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"DB연결이 끊겼거나 User 테이블이 존재하지 않음"}, status=status.HTTP_404_NOT_FOUND) #DB와 연결이 끊겼을 때
        if data is not None: #해당 이메일이 UserDB에 존재하는지 확인 (중복확인)
            if(len(userData.filter(email=data))) != 0: #중복확인 불 통과
                return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"이미 존재하는 이메일입니다."}, status=status.HTTP_200_OK)
            else: #중복확인 통과
                temp = getAuthenticate(data)
                sg = SendGridAPIClient(emailsetting.EMAIL_HOST_PASSWORD)
                message = Mail(

                    to_emails=str(data),
                    from_email=Email('bookkydevteam@gmail.com', "북키"),
                )
                message.template_id = 'd-7cb30c9512e34cbf83c3bdf6150f0a8e'
                message.dynamic_template_data = {
                    'code': str(temp),
                }
                
                sg.send(message)
                # send_mail('북키 서비스 인증 메일입니다.', content, 'bookkydevteam@gmail.com',[str(data)], fail_silently=False)
                return JsonResponse({'success':True, 'result':{'email' : data}, 'errorMessage':""}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"email 입력 값이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',  
    request_body=openapi.Schema(
        '해당 내용의 titile',
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema('사용자 email ID', type=openapi.TYPE_STRING),
            'code': openapi.Schema('인증번호', type=openapi.TYPE_INTEGER)
        },
        required=['email', 'code']  # 필수값을 지정 할 Schema를 입력해주면 된다.
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={}
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING),
            }
        )
    }
)
#Code확인
@api_view(['POST'])
def checkCode(request):
    exceptDict = None
    """
    인증코드 확인

# Body
```json
{
    "email": String,
    "code": Integer
}
```

# Response
```json
{
    "success": Boolean,
    "result": {},
    "errorMessage": String
}
```

    """
    data = JSONParser().parse(request)
    if(request.method == 'POST'):
        if checkAuthentication(data['email'], data['code']): 
            return JsonResponse({'success':True, 'result':exceptDict,'errorMessage':""}, status=status.HTTP_200_OK) #Code가 맞는경우
        else:
            return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"Code가 올바르지 않습니다."},status=status.HTTP_406_NOT_ACCEPTABLE) #Code가 틀렸을 경우

@swagger_auto_schema(
    method='post',  
    manual_parameters=[
        openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING),
        openapi.Parameter('refresh-token', openapi.IN_HEADER, description="갱신 토큰", type=openapi.TYPE_STRING)
        ],
    # 필수값을 지정 할 Schema를 입력해주면 된다.
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access_token': openapi.Schema('인가 토큰', type=openapi.TYPE_STRING)
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING),
            }
        )
    }
)
#AT토큰 갱신
@api_view(['POST'])
def refresh_token(request):
    exceptDict = None
    """
    토큰 갱신

# Header
```json
{
	"access-token" : String,
	"refresh-token" : String
}
```

# Response
```json
{
    "success": Boolean,
    "result": {"access_token": String},
    "errorMessage": String,
}
```
    """
    # AccessToken이 만료됬고, RefreshToken이 만료되지 않았을 때, AccessToken을 재발급 해주는 시나리오 
    if request.method == 'POST':
        if request.headers.get('refresh_token',None) is not None and request.headers.get('access_token', None) is not None: # request 헤더에 RefreshToken이라는 파라미터에 값이 실려 왔는가?
            refresh_access_token = re_generate_Token(request)
            if refresh_access_token == 2:
                return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"만료된 토큰입니다."}, status=status.HTTP_401_UNAUTHORIZED)  #RefreshToken의 기간이 지남
            elif refresh_access_token == 3:
                return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"유효하지 않은 토큰입니다."}, status=status.HTTP_403_FORBIDDEN) #RefreshToken의 형식이 잘못됨
            elif refresh_access_token == 4:
                return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"유효한 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST) #AccessToken의 만료기간이 남음
            elif refresh_access_token == 5:
                return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"DB가 존재하지 않거나, 연결이 끊겼습니다."}, status=status.HTTP_404_NOT_FOUND) #RefreshTokenStorage와의 연결이 끊김
            return JsonResponse({'success':True, 'result': {'access_token':str(refresh_access_token)}, 'errorMessage':""}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False,'result':exceptDict,'errorMessage':"access_token 혹은 refresh_token이 없습니다."},status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':str(request.method) + " 호출은 지원하지 않습니다."}, status=status.HTTP_405_METHOD_NOT_ALLOWED) #POST가 아닌 방식으로 접근 했을 경우

@swagger_auto_schema(
    method='post',  
    manual_parameters=[
        openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING),
        openapi.Parameter('refresh-token', openapi.IN_HEADER, description="갱신 토큰", type=openapi.TYPE_STRING)
        ],
    # 필수값을 지정 할 Schema를 입력해주면 된다.
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
#로그아웃
@api_view(['POST'])
def signOut(request):
    exceptDict = None
    """
    로그아웃

# Body
```json
{//headers
			"access-token" : String,  //접근 토큰
			"refresh-token" : String	//갱신 토큰
}
```

# Response
```json
{
    "success": Boolean,
    "result": {},
    "errorMessage": String
}
```

    """
    if request.method == "POST":
        if request.headers.get('access_token') is None:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"형식이 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
             userID = checkAuth_decodeToken(request)
             if userID == -1:
                 return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
             elif userID == -2:
                 return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_401_UNAUTHORIZED)
             else: 
                tempQuery = RefreshTokenStorage.objects.get(UID = userID)
                tempQuery.delete()
                return JsonResponse({'success':True, 'result':exceptDict, 'errorMessage':""}, status = status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('nickname',openapi.IN_QUERY,type=openapi.TYPE_STRING, description='닉네임')
    ],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'nickname':openapi.Schema(type=openapi.TYPE_STRING)
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
@api_view(['GET'])
def nicknameCheck(request):
    data = request.GET.get('nickname')
    # exceptDict = {'nickname':""}
    exceptDict = None
    if data is not None:
        if len(User.objects.filter(nickname=data)) == 0:
            return JsonResponse({'success':True, 'result':{'nickname':data}, 'errorMessage':""}, status = status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"존재하는 닉네임"}, status = status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"nickname이 존재하지 않음"}, status = status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        '이메일 인증을 무조건 진행하고 비밀번호 초기화로 진행',
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema('사용자 email ID', type=openapi.TYPE_STRING),
            'pwToken': openapi.Schema('비밀번호', type=openapi.TYPE_STRING)
        },
        required=['email', 'pwToken']  # 필수값을 지정 할 Schema를 입력해주면 된다.
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema('성공 메시지', type=openapi.TYPE_STRING),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
@api_view(['PUT'])
def initPassword(request): #비밀번호 초기화하는 API,비밀번호 찾기에 들어감 (이메일을 통해서 비밀번호 초기화 시작)
    flag = None
    exceptDict = None
    data = JSONParser().parse(request)
    if request.method == 'PUT':    
        userQuery = User.objects.get(email = data['email'])
        if len(data['pwToken']) >= 8 and userQuery.loginMethod == 0:
            userQuery.pwToken = setToken(data['pwToken'])
            userQuery.save()
            return JsonResponse({'success':True, 'result':"비밀번호 초기화 완료",'errorMessage':""}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success':True, 'result':"",'errorMessage':"비밀번호가 8자리가 아니거나, 북키회원이 아닌소셜 회원임"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description= "이메일 인증코드 전송 및 이메일 존재 확인",
    manual_parameters=[
        openapi.Parameter('email',openapi.IN_QUERY,type=openapi.TYPE_STRING, description='이메일'),
    ],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'email' : openapi.Schema('이메일', type=openapi.TYPE_STRING)
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
@api_view(['GET'])
def authenticateEmail(request):
    """
    이메일 인증코드 발급 & 이메일이 존재하는지 확인

    - 인증코드 만료시간 3분임

# Response
```json
{
    "success": Boolean, //False 이면 중복
    "result": {
        "email": String
    },
    "errorMessage": String
}
```

    """
    
    if(request.method == 'GET'):
        # exceptDict = {'email':""}
        exceptDict = None
        try:
            data = request.GET.get('email')
            userData = User.objects.filter(email=data) 
        except User.DoesNotExist:
            return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"DB연결이 끊겼거나 User 테이블이 존재하지 않음"}, status=status.HTTP_404_NOT_FOUND) #DB와 연결이 끊겼을 때
        if data is not None: #해당 이메일이 UserDB에 존재하는지 확인 (중복확인)
            if(len(userData.filter(email=data))) == 0: #중복확인 불 통과
                return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"존재하지 않는 이메일입니다."}, status=status.HTTP_200_OK)
            else: #중복확인 통과
                temp = getAuthenticate(data)
                sg = SendGridAPIClient(emailsetting.EMAIL_HOST_PASSWORD)
                message = Mail(
                    to_emails=str(data),
                    from_email=Email('bookkydevteam@gmail.com', "북키"),
                )
                message.template_id = 'd-7cb30c9512e34cbf83c3bdf6150f0a8e'
                message.dynamic_template_data = {
                    'code': str(temp),
                }
                
                sg.send(message)
                # send_mail('북키 서비스 인증 메일입니다.', content, 'bookkydevteam@gmail.com',[str(data)], fail_silently=False) #인증코드 발송 코드 //Todo: 인증메일 양식 만들어야함
                return JsonResponse({'success':True, 'result':{'email' : data}, 'errorMessage':""}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"email 입력 값이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',  
    manual_parameters=[
        openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING),
        ],
    # 필수값을 지정 할 Schema를 입력해주면 된다.
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema('푸쉬알림 허용여부',type=openapi.TYPE_BOOLEAN),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
#push알림 허용
@api_view(['POST'])
def checkPush(request):
    exceptDict = None
    if request.method == "POST":
        if request.headers.get('access_token') is None:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"형식이 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            userID = checkAuth_decodeToken(request)
            if userID == -1:
                return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
            elif userID == -2:
                return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_401_UNAUTHORIZED)
            else: 
                userQuery = User.objects.get(UID = userID)
                if userQuery.pushNoti == True :
                    userQuery.pushNoti = False
                else:
                    userQuery.pushNoti = True
                userQuery.save()
                
                return JsonResponse({'success':True, 'result':userQuery.pushNoti, 'errorMessage':""}, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='post',  
    manual_parameters=[
        openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING),
        ],
    request_body=openapi.Schema(
        '푸쉬알림 토큰 등록, 재등록도 포함',
        type=openapi.TYPE_OBJECT,
        properties={
            'pushToken': openapi.Schema('FCM 푸쉬 토큰', type=openapi.TYPE_STRING),
        },
        required=['pushToken']  # 필수값을 지정 할 Schema를 입력해주면 된다.
    ),
    # 필수값을 지정 할 Schema를 입력해주면 된다.
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema('푸쉬토큰',type=openapi.TYPE_STRING),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
#push토큰 등록
@api_view(['POST'])
def registPush(request):
    exceptDict = None
    if request.method == "POST":
        if request.headers.get('access_token') is None:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"형식이 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            userID = checkAuth_decodeToken(request)
            if userID == -1:
                return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
            elif userID == -2:
                return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_401_UNAUTHORIZED)
            else: 
                parsedData = JSONParser().parse(request)
                userQuery = User.objects.get(UID = userID)
                if parsedData['pushToken'] is not None:
                    userQuery.pushToken = parsedData['pushToken']
                    userQuery.save()
                    return JsonResponse({'success':True, 'result':userQuery.pushToken, 'errorMessage':""}, status = status.HTTP_200_OK)
                else:
                    return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"푸쉬토큰이 없습니다 Body를 확인하세요."}, status = status.HTTP_400_BAD_REQUEST)