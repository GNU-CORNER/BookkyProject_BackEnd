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
                            'PID':openapi.Schema('포스트 번호', type=openapi.TYPE_INTEGER),
                            'title':openapi.Schema('게시글 제목', type=openapi.TYPE_INTEGER),
                            'contents':openapi.Schema('게시글 내용', type=openapi.TYPE_STRING),
                            }
                        )),
                         'userData' : openapi.Schema('작성자 목록', type=openapi.TYPE_ARRAY, items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'nickname':openapi.Schema('사용자 닉네임',type=openapi.TYPE_STRING),
                                'thumbnail':openapi.Schema('사용자 프로필 사진', type=openapi.TYPE_STRING)
                            }
                        )),
                         'subData' : openapi.Schema('기타 데이터 목록', type=openapi.TYPE_ARRAY, items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'commentCnt':openapi.Schema('댓글 갯수',type=openapi.TYPE_INTEGER),
                                'like':openapi.Schema('좋아요 수', type=openapi.TYPE_INTEGER)
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
def getCommunityPostList(request,slug):
    exceptDict = None
    if request.method == 'GET':
        try:
            if slug == "0":        # 쿼리에서 createdAt 으로 정렬 후 ? updateAt은? updateAt으로 해야겟네
                CommunityQuery = AnyCommunity.objects.order_by('createAt')
            elif slug == "1":
                CommunityQuery = MarketCommunity.objects.order_by('createAt')
            elif slug == "2":
                CommunityQuery = QnACommunity.objects.order_by('createAt')
            else:
                return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"잘못된 slug 입니다."}, status=status.HTTP_404_NOT_FOUND)
        except Book.DoesNotExist:
            return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"해당 Community에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"}, status=status.HTTP_404_NOT_FOUND)


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
            endpagination = len(Posts)
        Posts = Posts[startpagination : endpagination]

        userData = []
        subData = []

        for i in range(len(Posts)):
            tempuserData = dict()
            tempuserData['nickname']=Posts[i].UID.nickname
            tempuserData['thumbnail']=Posts[i].UID.thumbnail
            userData.append(tempuserData)

            tempsubData = dict()
            if slug == "0":
                commentData = AnyComment.objects.filter(APID = Posts[i].APID)
            
            tempsubData['commentCnt'] = len(commentData)
            tempsubData['likeCnt'] = len(Posts[i].like)
            subData.append(tempsubData)
            

        if slug == "0":
            serializer = AnyCommunitySerializer(Posts, many=True)
        elif slug == "1":
            serializer = MarketCommunitySerializer(Posts, many=True)
        elif slug == "2":
            serializer = QnACommunitySerializer(Posts, many=True)
        
        return JsonResponse({
            'success':True,
            'result' :{'postList':serializer.data, 'userData':userData, 'subData':subData},
            'errorMessage':""
            }, 
            status=status.HTTP_200_OK)
    

@api_view(['GET'])
def getCommunityPostdetail(request,slug1,slug2):
    exceptDict = None
    if request.method == 'GET':
        try:
            if slug1 == "0":
                CommunityQuery = AnyCommunity.objects.order_by('createAt')
            elif slug1 == "1":
                CommunityQuery = MarketCommunity.objects.order_by('createAt')
            elif slug1 == "2":
                CommunityQuery = QnACommunity.objects.order_by('createAt')
            else:
                return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"잘못된 slug 입니다."}, status=status.HTTP_404_NOT_FOUND)
        except Book.DoesNotExist:
            return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"해당 Community에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"}, status=status.HTTP_404_NOT_FOUND)

        postuserData = []
        if slug1 == "0":
            PostData = AnyCommunity.objects.filter(APID = slug2)
            serializer = AnyCommunityDetailSerializer(PostData,many=True)
            commentData = AnyComment.objects.filter(APID = PostData[0].APID)
            commentserializer = AnyCommentSerializer(commentData,many=True)
            tempuserData = dict()
            tempuserData['nickname']=PostData[0].UID.nickname
            tempuserData['thumbnail']=PostData[0].UID.thumbnail
            postuserData.append(tempuserData)

        commentuserData = []

        for i in range(len(commentData)):
            tempcommentData = dict()
            tempcommentData['nickname']=commentData[i].UID.nickname
            tempcommentData['thumbnail']=commentData[i].UID.thumbnail
            commentuserData.append(tempcommentData)
    
        return JsonResponse({
            'success':True,
            'result' :{'postdata':serializer.data,'postuserdata': postuserData, 'commentdata':commentserializer.data, 'commentuserdata':commentuserData},
            'errorMessage':""
        }, 
        status=status.HTTP_200_OK)

    else:
        return JsonResponse({'success':False,'result' : exceptDict, 'errorMessage':str(request.method) + " 호출은 지원하지 않습니다."}, status=status.HTTP_403_FORBIDDEN)


# @api_view(['POST'])
# def writeCommunityPost(request,slug):
#     # AT가 들어오면 누군지 내가 알아내야함
    
#     try:
#         data = JSONParser().parse(request)
#         flag = checkAuth_decodeToken(request)
#     except User.DoesNotExist: #User 데이터베이스가 존재하지 않을 때, 혹은 DB와의 연결이 끊겼을 때 출력
#         return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"User에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"},status=status.HTTP_404_NOT_FOUND)

#     exceptDict = None

#     if flag == 0:
#         return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
#     elif flag == 1:
#         return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
#     elif flag == 2:
#         return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_403_FORBIDDEN)
    
    # userData = User.objects
    # if data['nickname'] is not None:
    #     if len(userData.filter(nickname = data['nickname'])) != 0: # 이게 근데 그 nickname 같은 사람인지 어떻게 아노?
    #         users = userData.get(email=data['nickname'])
    #         if data['loginMethod'] is not None:
    #             if(checkToken(data['pwToken'], users)): #로그인 성공
    #                 filteredData = userData.filter(email=data['email'])
    #                 serializer = UserRegisterSerializer(filteredData, many=True)
    #                 accessToken = get_access(users.UID)
    #                 refreshToken = get_refreshToken(users.UID)
    #                 if refreshToken :
    #                     tempData = RefreshTokenStorage.objects.filter(UID =users.UID)
    #                     refreshToken = tempData[0].refresh_token
    #                     temp = serializer.data[0]
    #                     del temp['pwToken']
    #                     if temp['tag_array'] is not None:
    #                         tempTag = []
    #                         tagQuery = Tag.objects
    #                         for i in temp['tag_array']:
    #                             temps = tagQuery.get(TID = i)                                
    #                             tempTag.append(temps.nameTag)
    #                         temp['tag_array'] = tempTag
    #                     return JsonResponse({"success" : True, "result": {'userData':temp, 'access_token':str(accessToken), 'refresh_token' : str(refreshToken)}, 'errorMessage':""}, status=status.HTTP_200_OK)
    #                 elif refreshToken == 500:
    #                     return JsonResponse({'success':False, "result": exceptDict, 'errorMessage':"serverError"}, status=status.HTTP_404_NOT_FOUND)
    #             else: #로그인 비밀번호 틀림
    #                 return JsonResponse({"success" : False, "result": exceptDict, 'errorMessage':"비밀번호가 틀렸습니다."}, status=status.HTTP_400_BAD_REQUEST)
    #         else:
    #             return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"LoginMethod가 없습니다.."},status=status.HTTP_400_BAD_REQUEST)
    #     else: #해당 이메일 정보 없음
    #         return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"해당하는 유저가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    #         #Github 로그인
    # else:
    #     return JsonResponse({'success' : False, "result": exceptDict,'errorMessage':"email정보가 없음"}, status=status.HTTP_400_BAD_REQUEST)