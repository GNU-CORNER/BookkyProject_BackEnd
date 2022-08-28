from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg import openapi
from urllib import parse

from bookky.auth.auth import checkAuth_decodeToken
from bookky_backend import settings
from bookky.models import TempBook, FavoriteBook, TagModel, Review, User
from bookky.serializers.bookserializers import BookPostSerializer, BookGetSerializer, BookSearchSerializer, BookSimpleSerializer
from bookky.serializers.reviewserializers import ReviewGetSerializer
from bookky.views.recommendview import todayRecommendBooks
from bookky.auth.auth import authValidation
from django.db.models import Q
from firebase_admin import messaging
import requests
import datetime
import urllib.request
import json
import time


@api_view(['POST'])
def put_device_ospns_token(request):
    flag = checkAuth_decodeToken(request) #AT 체크
    exceptDict = None
    if flag == 0:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    elif flag == -1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == -2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        try:
            userQuery = User.objects.get(UID = flag)
            parseData = JSONParser().parse(request)
            userQuery.pushToken = parseData['push-token']
            userQuery.save()
        except User.DoesNotExist:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"DB와의 연결이 끊어졌습니다."}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

def send_push_alert(uid, message):
    # This registration token comes from the client FCM SDKs.
    # registration_token = 'fyuCGw6zzk_MvqHd7gm8Ul:APA91bH5Ws9_RDCy5781MhLVNY089H8inyzysPVfzW2kLutnXwg2rgTK14rO1JlirYLKpcM3-tHcXKNPF0BU7ESMlUjB6a-NESP458KOPKOSZzKIoLomD7dSCiyYKb5Xmjik3DZhVf1N'
    userQuery = User.objects.get(UID = uid)
    if userQuery.pushNoti and userQuery.pushToken is not None :
        token = userQuery.pushToken
        registration_token = token
        # See documentation on defining a message payload.
        message = messaging.Message(
        notification=messaging.Notification(
        title=str(userQuery.nickname) + '님 안녕하세요 북키에요!',
        body=str(PushMessageObject.content),
            ),
        token=registration_token,
            )
        response = messaging.send(message)
        # Response is a message ID string.

class PushMessageObject:
    def __init__(title, content):
        self.title = title
        self.content = content