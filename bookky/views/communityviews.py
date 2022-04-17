from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg import openapi
from time import sleep

from bookky.auth.auth import checkAuth_decodeToken
from bookky_backend import settings
from bookky.models import User, Book, AnyComment, AnyCommunity, QnACommunity, QnAComment, MarketComment, MarketCommunity, HotCommunity, RefreshTokenStorage, Tag
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
            if slug1 == "0":
                tempcommentData['CID']=commentData[i].ACID
            tempcommentData['parentID']=commentData[i].parentID
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


@swagger_auto_schema(
    method='post',  
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
       request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'title': openapi.Schema('글 제목', type=openapi.TYPE_STRING),
                    'contents': openapi.Schema('글 내용', type=openapi.TYPE_STRING),        
                    'BID': openapi.Schema('책 BID', type=openapi.TYPE_INTEGER),
        },
        required=['title','contents']
    ),  # 필수값을 지정 할 Schema를 입력해주면 된다.
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema('', type=openapi.TYPE_STRING  ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING),
            }
        )
    }
)


@api_view(['POST'])
def writeCommunityPost(request,slug):
    exceptDict = None   
    if request.headers.get('access_token') is None:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"형식이 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        userID = checkAuth_decodeToken(request)
        if userID == 1:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        elif userID == 2:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        else:                            
            if (request.method == 'POST'):
                data = JSONParser().parse(request)
                # userID = UID
                userData = User.objects.filter(UID = userID)
                
                if len(userData) != 0:
                    userNickname = userData[0].nickname
                    data['UID']=userData[0].UID
                    data['createAt']=str(datetime.datetime.utcnow())
                    data['views']=0
                    if slug == "0":
                        postSerializer = AnyCommunityDetailSerializer(data = data)


                    if postSerializer.is_valid():
                        postSerializer.save()
                        return JsonResponse({
                        'success':True,
                        'result' :{},
                        'errorMessage':"저장댐"
                        })
                    else:
                        return JsonResponse({
                        'success':False,
                        'result' :{},
                        'errorMessage':postSerializer.errors
                        })
                else:
                    return JsonResponse({
                        'success':False,
                        'result' :{},
                        'errorMessage':"유저 없음"
                        })
            else:
                return JsonResponse({
                        'success':False,
                        'result' :{},
                        'errorMessage':"Post가 아님"
                        })


@swagger_auto_schema(
    method='post',  
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
       request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'comment': openapi.Schema('댓글 내용', type=openapi.TYPE_STRING),
                    'parentID': openapi.Schema('대댓글 ID', type=openapi.TYPE_INTEGER),
                    'PID': openapi.Schema('POST ID', type=openapi.TYPE_INTEGER),
        },
        required=['contents','parentID','PID']
    ),  # 필수값을 지정 할 Schema를 입력해주면 된다.
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema('', type=openapi.TYPE_STRING  ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING),
            }
        )
    }
)


@api_view(['POST'])
def writeCommunityComment(request,slug):
    exceptDict = None   
    if request.headers.get('access_token') is None:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"형식이 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        userID = checkAuth_decodeToken(request)
        if userID == 1:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        elif userID == 2:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        else:                
            
            if (request.method == 'POST'):
                data = JSONParser().parse(request)
                postData=[]
                if slug == "0":
                    postData = AnyCommunity.objects.filter(APID = data['PID'])
    
                userData = User.objects.filter(UID = userID)
                if len(postData) != 0 and len(userData) !=0:
                    userNickname = userData[0].nickname
                    data['UID']=userData[0].UID
                    data['createAt']=str(datetime.datetime.utcnow())
                    del data['PID']
                    if slug == "0":
                        data['APID']=postData[0].APID
                        print(data)
                        postSerializer = AnyCommentSerializer(data = data)


                    if postSerializer.is_valid():
                        postSerializer.save()
                        return JsonResponse({
                        'success':True,
                        'result' :{},
                        'errorMessage':"저장댐"
                        })
                    else:
                        return JsonResponse({
                        'success':False,
                        'result' :{},
                        'errorMessage':postSerializer.errors
                        })
                else:
                    return JsonResponse({
                        'success':False,
                        'result' :{},
                        'errorMessage':"유저 없음"
                        })
            else:
                return JsonResponse({
                        'success':False,
                        'result' :{},
                        'errorMessage':"Post가 아님"
                        })


@swagger_auto_schema(
    method='delete',  
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
       request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'PID': openapi.Schema('POST ID', type=openapi.TYPE_INTEGER),
        },
        required=['PID']
    ),  # 필수값을 지정 할 Schema를 입력해주면 된다.
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema('', type=openapi.TYPE_STRING  ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING),
            }
        )
    }
)


@api_view(['DELETE'])
def delteCommunityPost(request,slug):
    exceptDict = None   
    if request.headers.get('access_token') is None:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"형식이 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        userID = checkAuth_decodeToken(request)
        if userID == 1:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        elif userID == 2:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        else:               
            if (request.method == 'DELETE'):
                data = JSONParser().parse(request)
                if slug == "0":
                    postData = AnyCommunity.objects.filter(APID = data['PID'])
                elif slug == "1":
                    postData = MarketCommunity.objects.filter(MPID = data['PID'])
                elif slug == "2":
                    postData = QnACommunity.objects.filter(QPID = data['PID'])
                else:
                    return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"잘못된 slug"}, safe=False, status=status.HTTP_403_FORBIDDEN)

                if len(postData) == 0 :
                    return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"해당 포스트의 정보 없음"}, safe=False, status=status.HTTP_204_NO_CONTENT)
                else:
                    if postData[0].UID.UID == userID:
                        postData.delete()
                        return JsonResponse({'success':True, 'result':"성공", 'errorMessage':""},status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"해당 유저의 글이 아닙니다."}, safe=False, status=status.HTTP_403_FORBIDDEN)



@swagger_auto_schema(
    method='delete',  
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
       request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'CID': openapi.Schema('Comment ID', type=openapi.TYPE_INTEGER),
        },
        required=['CID']
    ),  # 필수값을 지정 할 Schema를 입력해주면 된다.
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema('', type=openapi.TYPE_STRING  ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING),
            }
        )
    }
)

@api_view(['DELETE'])
def delteCommunityComment(request,slug):
    exceptDict = None   
    if request.headers.get('access_token') is None:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"형식이 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        userID = checkAuth_decodeToken(request)
        if userID == 1:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        elif userID == 2:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        else:               
            if (request.method == 'DELETE'):
                data = JSONParser().parse(request)
                if slug == "0":
                    commentData = AnyComment.objects.filter(ACID = data['CID'])
                elif slug == "1":
                    commentData = MarketComment.objects.filter(MCID = data['CID'])
                elif slug == "2":
                    commentData = QnACComment.objects.filter(QCID = data['CID'])
                else:
                    return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"잘못된 slug"}, safe=False, status=status.HTTP_403_FORBIDDEN)

                if len(commentData) == 0 :
                    return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"해당 포스트의 정보 없음"}, safe=False, status=status.HTTP_204_NO_CONTENT)
                else:
                    if commentData[0].UID.UID == userID:
                        commentData.delete()
                        return JsonResponse({'success':True, 'result':"성공", 'errorMessage':""},status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"해당 유저의 댓글이 아닙니다."}, safe=False, status=status.HTTP_403_FORBIDDEN)

