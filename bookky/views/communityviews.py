from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg import openapi

from bookky.auth.auth import checkAuth_decodeToken
from bookky_backend import settings
from bookky.models import User, Book, AnyComment, AnyCommunity, QnACommunity, QnAComment, MarketComment, MarketCommunity, HotCommunity
from bookky.serializers.communityserializers import *
from bookky.auth.auth import authValidation
from django.db.models import Q

import requests
import datetime
import urllib.request
import json
import time

@swagger_auto_schema(
    method='get',
    operation_description= "slug => 0 = '자유게시판', 1 = '장터게시판', 2 = 'QnA게시판'",
    manual_parameters=[
        openapi.Parameter('quantity',openapi.IN_QUERY,type=openapi.TYPE_INTEGER, description='원하는 수량'),
        openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='원하는 페이지'),
        openapi.Parameter('access-token', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='회원이라면 토큰 넣고 비회원이면 넣지 않는다.')
    ],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'postList' : openapi.Schema('포스트 목록', type=openapi.TYPE_ARRAY, items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                            'contents':openapi.Schema('책 저자', type=openapi.TYPE_STRING),
                            'postImage':openapi.Schema('책 ISBN코드', type=openapi.TYPE_STRING),
                            }
                        ))
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)


@api_view(['GET'])
def getAnyCommunity(request,slug):
    exceptDict = None
    if request.method == 'GET':
        try:
            if slug == "0":
                CommunityQuery = AnyCommunity.objects
            elif slug == "1":
                CommunityQuery = MarketCommunity.objects
            elif slug == "2":
                CommunityQuery = QnACommunity.objects
            else:
                return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"잘못된 slug 입니다."}, status=status.HTTP_404_NOT_FOUND)
        except Book.DoesNotExist:
            return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"AnyCommunity에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"}, status=status.HTTP_404_NOT_FOUND)

        quantity = 20 #기본 quntity 값은 20개
        startpagination = 0 #기본 startpagination 값은 0
        endpagination = quantity #기본 endpagination 값은 qunatity값과 동일, page 값이 들어오면 pagination 지원
        Posts = CommunityQuery.all()
        if request.GET.get('quantity') is not None: #URL에 'quantity' Query가 들어있으면 값 입력
            quantity = int(request.GET.get('quantity')) 
        if request.GET.get('page') is not None: #URL에 'page' Query가 들어있으면 값 입력
            startpagination = (int(request.GET.get('page')) - 1) * quantity
            endpagination = int(request.GET.get('page')) * quantity
            if startpagination > len(Posts):
                startpagination = startpagination - len(Posts)
            if endpagination > len(Posts):
                endpagination = len(Posts) - 1
        Posts = Posts[startpagination : endpagination]   
        if slug == "0":
            serializer = AnyCommunitySerializer(Posts, many=True)
        elif slug == "1":
            serializer = MarketCommunitySerializer(Posts, many=True)
        elif slug == "2":
            serializer = QnACommunitySerializer(Posts, many=True)
        
        return JsonResponse({
            'success':True,
            'result' :{'postList':serializer.data},
            'errorMessage':""
            }, 
            status=status.HTTP_200_OK)
    else:
        return JsonResponse({'success':False,'result' : exceptDict, 'errorMessage':str(request.method) + " 호출은 지원하지 않습니다."}, status=status.HTTP_403_FORBIDDEN)