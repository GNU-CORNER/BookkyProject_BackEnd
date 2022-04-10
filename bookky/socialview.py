from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
import urllib3
from .models import User, RefreshTokenStorage
from .userserializers import UserRegisterSerializer
from .auth import setToken, get_access, get_refreshToken

#소셜 회원가입
@api_view(['POST'])
def socialSignup(request):
    data = JSONParser().parse(request)
    if data['loginMethod'] == 1: # Github
        print(1)
    elif data['loginMethod'] == 2: #Google
        print(1)
    elif data['loginMethod'] == 3: #Apple
        print(1)

@api_view(['GET'])
def socialCallbackGoogle(request):
    code = request.GET.get('code')
    data = JSONParser().parse(request)
    print(data)
    print(code)
    return JsonResponse({'success':True},status=status.HTTP_200_OK)

@api_view(['POST'])
def socialCallbackGitHub(request):
    data = JSONParser().parse(request)
    print(data)
    return JsonResponse({'success':True},status=status.HTTP_200_OK)
@api_view(['POST'])
def socialCallbackApple(request):
    data = JSONParser().parse(request)
    print(data)
    return JsonResponse({'success':True},status=status.HTTP_200_OK)