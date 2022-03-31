from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from .models import User
from .userserializers import UserRegisterSerializer


def socialEmailCheck(email):
    if len(User.objects.filter(email = email)) == 0:
        return True
    else:
        return False
    
#소셜 로그인
@api_view(['POST'])
def socialLogin(request):
    if request.method == 'POST':
        data = JSONParser.parse(request)
        userData = User.objects
        if(len(userData.filter(email=data['email']))) == 0: #회원가입 request에 넘어온 UID값과 DB안의 UID와 비교하여 존재하지 않으면, 회원가입으로 생각함
            #소셜 로그인의 토큰을 PW 토큰으로 사용한다.
            userSerializer = UserRegisterSerializer(data = data)
            if userSerializer.is_valid():
                userSerializer.save()
                return JsonResponse({'success': True, 'result':userSerializer.data,'errorMessage':""}, status = status.HTTP_201_CREATED)
            
            else:
                return JsonResponse({'success' : False, "result": {}}, status=status.HTTP_400_BAD_REQUEST)
            
