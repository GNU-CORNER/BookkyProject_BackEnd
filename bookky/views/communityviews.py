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
from bookky.models import User, TempBook, AnyComment, AnyCommunity, QnACommunity, QnAComment, MarketComment, MarketCommunity, HotCommunity, RefreshTokenStorage, TagModel
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
                            'title':openapi.Schema('게시글 제목', type=openapi.TYPE_STRING),
                            'contents':openapi.Schema('게시글 내용', type=openapi.TYPE_STRING),
                            'commentCnt':openapi.Schema('댓글 갯수',type=openapi.TYPE_INTEGER),
                            'likeCnt':openapi.Schema('좋아요 수', type=openapi.TYPE_INTEGER)
                            }
                        )),
                        'total_size' : openapi.Schema('포스트 총 개수', type=openapi.TYPE_INTEGER)
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
                CommunityQuery = AnyCommunity.objects.order_by('-createAt')
            elif slug == "1":
                CommunityQuery = MarketCommunity.objects.order_by('-createAt')
            else:
                return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"잘못된 slug 입니다."}, status=status.HTTP_400_BAD_REQUEST)
        except TempBook.DoesNotExist:
            return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"해당 Community에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"}, status=status.HTTP_404_NOT_FOUND)


        quantity = 20 #기본 quntity 값은 20개
        startpagination = 0 #기본 startpagination 값은 0
        endpagination = quantity #기본 endpagination 값은 qunatity값과 동일, page 값이 들어오면 pagination 지원
        Posts = CommunityQuery.all()
        total_size = len(Posts)
        if request.GET.get('quantity') is not None: #URL에 'quantity' Query가 들어있으면 값 입력
            quantity = int(request.GET.get('quantity')) 

        if request.GET.get('page') is not None: #URL에 'page' Query가 들어있으면 값 입력
            startpagination = (int(request.GET.get('page')) - 1) * quantity
            endpagination = int(request.GET.get('page')) * quantity

        if startpagination > len(Posts):
            startpagination = len(Posts)

        if endpagination > len(Posts):
            endpagination = len(Posts)

        Posts = Posts[startpagination : endpagination]

        if slug == "0":
            serializer = AnyCommunitySerializer(Posts,many=True)
        elif slug == "1":
            serializer = MarketCommunitySerializer(Posts,many=True)
        userData = []
        subData = []

        for i in range(len(Posts)):
            if slug == "0":
                serializer.data[i]['commentCnt']=len(AnyComment.objects.filter(APID = Posts[i].APID))
            elif slug == "1":
                serializer.data[i]['commentCnt']=len(MarketComment.objects.filter(MPID = Posts[i].MPID))

            serializer.data[i]['likeCnt']=len(Posts[i].like)
            del serializer.data[i]['like']
            if slug == "0":
                serializer.data[i]['PID'] = serializer.data[i]['APID']
                del serializer.data[i]['APID']            
            elif slug == "1":
                serializer.data[i]['PID'] = serializer.data[i]['MPID']
                del serializer.data[i]['MPID']            

        return JsonResponse({
            'success':True,
            'result' :{'postList':serializer.data, 'total_size':total_size}, 
            'errorMessage':""
            }, 
            status=status.HTTP_200_OK)



@swagger_auto_schema(
    method='get',
    operation_description= "slug1 => 0 = '자유게시판', 1 = '장터게시판', 2 = 'QnA게시판'  , slug2 => PID",
    manual_parameters=[
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
                        'postdata' : openapi.Schema('포스트 정보', type=openapi.TYPE_ARRAY, items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                            'title':openapi.Schema('게시글 제목', type=openapi.TYPE_INTEGER),
                            'contents':openapi.Schema('게시글 내용', type=openapi.TYPE_STRING),
                            'views':openapi.Schema('방문 횟수', type=openapi.TYPE_STRING),
                            'updateAt':openapi.Schema('수정 날짜', type=openapi.TYPE_STRING),
                            'like':openapi.Schema('좋아요', type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
                            'nickname':openapi.Schema('사용자 닉네임',type=openapi.TYPE_STRING),
                            'thumbnail':openapi.Schema('사용자 프로필 사진', type=openapi.TYPE_STRING),
                            'isAccessible':openapi.Schema('접근 가능', type=openapi.TYPE_BOOLEAN)
                            }
                        )),
                         'commentdata' : openapi.Schema('댓글 정보', type=openapi.TYPE_ARRAY, items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'comment':openapi.Schema('댓글 내용', type=openapi.TYPE_STRING),
                                'updateAt':openapi.Schema('수정 날짜', type=openapi.TYPE_STRING),
                                'like':openapi.Schema('좋아요', type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
                                'nickname':openapi.Schema('댓글 작성자 닉네임',type=openapi.TYPE_STRING),
                                'thumbnail':openapi.Schema('댓글 작성자 사진', type=openapi.TYPE_STRING),
                                'isAccessible':openapi.Schema('접근 가능', type=openapi.TYPE_BOOLEAN),
                                'childComment' : openapi.Schema('대댓글 정보', type=openapi.TYPE_ARRAY, items=openapi.Items(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                    'comment':openapi.Schema('대댓글 내용', type=openapi.TYPE_STRING),
                                    'updateAt':openapi.Schema('수정 날짜', type=openapi.TYPE_STRING),
                                    'like':openapi.Schema('좋아요', type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
                                    'nickname':openapi.Schema('대댓글 작성자 닉네임',type=openapi.TYPE_STRING),
                                    'thumbnail':openapi.Schema('대댓글 작성자 사진', type=openapi.TYPE_STRING),
                                    'isAccessible':openapi.Schema('접근 가능', type=openapi.TYPE_BOOLEAN)
                                    }
                                ))
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
def getCommunityPostdetail(request,slug1,slug2):
    flag = checkAuth_decodeToken(request)
    exceptDict = None
    if flag == 0:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    elif flag == -1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == -2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        try:
            if slug1 == "0":
                PostData = AnyCommunity.objects.filter(APID = slug2)
                serializer = AnyCommunityDetailSerializer(PostData,many=True)
                commentData = AnyComment.objects.filter(APID = PostData[0].APID).order_by('updateAt')
                commentserializer = AnyCommentSerializer(commentData,many=True)
                

            elif slug1 == "1":
                PostData = MarketCommunity.objects.filter(MPID = slug2)
                serializer = MarketCommunityDetailSerializer(PostData,many=True)
                commentData = MarketComment.objects.filter(MPID = PostData[0].MPID).order_by('updateAt')
                commentserializer = MarketCommentSerializer(commentData,many=True)
                
            else:
                return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"잘못된 slug 입니다."}, status=status.HTTP_404_NOT_FOUND)
        except TempBook.DoesNotExist:
            return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"해당 Community에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"}, status=status.HTTP_404_NOT_FOUND)

        postuserData = []
        RcommentData = list()
        commentCnt= len(commentData)
        
        k = 0
        for i in commentserializer.data:
            i["nickname"]=commentData[k].UID.nickname
            i["thumbnail"]=commentData[k].UID.thumbnail
            if commentData[k].UID.UID == flag:
                i["isAccessible"] = True
            else:
                i["isAccessible"] = False
            if slug1 == "0":
                i["CID"] = i["ACID"]
                del i["ACID"]
                del i["APID"]
            
            elif slug1 == "1":
                i["CID"] = i["MCID"]
                del i["MCID"]
                del i["MPID"]

            if i["parentID"] == 0:
                i["childComment"] = list()
                RcommentData.append(i)
            else:
                for j in RcommentData:
                    if i["parentID"] == j["CID"]:
                        del i["parentID"]
                        del i["UID"]
                        j["childComment"].append(i)
                        break
            k = k + 1
        
        for i in RcommentData:
            del i["parentID"]
            del i["UID"]
        
        serializer.data[0]['nickname']=PostData[0].UID.nickname
        serializer.data[0]['thumbnail']=PostData[0].UID.thumbnail
        if serializer.data[0]['UID'] == flag:
            serializer.data[0]['isAccessible'] = True
        else:
            serializer.data[0]['isAccessible'] = False
        del serializer.data[0]['UID']
                
        return JsonResponse({
            'success':True,
            'result' :{'postdata':serializer.data[0],'commentdata':RcommentData, 'commentCnt':commentCnt},
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
                    'TBID': openapi.Schema('책 TBID', type=openapi.TYPE_INTEGER),
                    'parentID': openapi.Schema('답글 PID', type=openapi.TYPE_INTEGER),
        },
        required=['title','contents']
    ),  # 필수값을 지정 할 Schema를 입력해주면 된다.
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema('결과', type=openapi.TYPE_STRING  ),
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
        if userID == -1:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        elif userID == -2:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_401_UNAUTHORIZED)
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

                    elif slug == "1":
                        postSerializer = MarketCommunityDetailSerializer(data = data)

                    elif slug == "2":
                        postSerializer = QnACommunityDetailSerializer(data = data)

                    if postSerializer.is_valid():
                        postSerializer.save()
                        return JsonResponse({
                        'success':True,
                        'result' :"글 작성 완료",
                        'errorMessage':""
                        },status=status.HTTP_201_CREATED)
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
        properties=
        {           'comment': openapi.Schema('댓글 내용', type=openapi.TYPE_STRING),
                    'parentID': openapi.Schema('대댓글 ID', type=openapi.TYPE_INTEGER),
                    'PID': openapi.Schema('POST ID', type=openapi.TYPE_INTEGER),
        },
        required=['contents','parentID','PID']
    ),  # 필수값을 지정 할 Schema를 입력해주면 된다.
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=
            {
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema('결과', type=openapi.TYPE_STRING  ),
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
        if userID == -1:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        elif userID == -2:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_401_UNAUTHORIZED)
        else:                
            
            if (request.method == 'POST'):
                data = JSONParser().parse(request)
                postData=[]
                
                if slug == "0":
                    postData = AnyCommunity.objects.filter(APID = data['PID'])
                
                elif slug == "1":
                    postData = MarketCommunity.objects.filter(MPID = data['PID'])

                elif slug == "2":
                    postData = QnACommunity.objects.filter(QPID = data['PID'])

                userData = User.objects.filter(UID = userID)                
                
                if len(postData) != 0 and len(userData) !=0:
                    userNickname = userData[0].nickname
                    data['UID']=userData[0].UID
                    data['createAt']=str(datetime.datetime.utcnow())
                    del data['PID']
                    if slug == "0":
                        data['APID']=postData[0].APID
                        postSerializer = AnyCommentSerializer(data = data)

                    elif slug == "1":
                        data['MPID']=postData[0].MPID
                        postSerializer = MarketCommentSerializer(data = data)

                    elif slug == "2":
                        data['QPID']=postData[0].QPID
                        postSerializer = QnACommentSerializer(data = data)


                    if postSerializer.is_valid():
                        postSerializer.save()
                        return JsonResponse({
                        'success':True,
                        'result' :"댓글 작성 완료",
                        'errorMessage':""
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
                'result': openapi.Schema('결과', type=openapi.TYPE_STRING  ),
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
        if userID == -1:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        elif userID == -2:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_401_UNAUTHORIZED)
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
                    return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"잘못된 slug"}, safe=False, status=status.HTTP_400_BAD_REQUEST)

                if len(postData) == 0 :
                    return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"해당 포스트의 정보 없음"}, safe=False, status=status.HTTP_204_NO_CONTENT)
                else:
                    if postData[0].UID.UID == userID:
                        postData.delete()
                        return JsonResponse({'success':True, 'result':"글 삭제 완료", 'errorMessage':""},status=status.HTTP_200_OK)
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
                'result': openapi.Schema('결과', type=openapi.TYPE_STRING  ),
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
        if userID == -1:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        elif userID == -2:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_401_UNAUTHORIZED)
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
                    return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"잘못된 slug"}, safe=False, status=status.HTTP_400_BAD_REQUEST)

                if len(commentData) == 0 :
                    return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"해당 포스트의 정보 없음"}, safe=False, status=status.HTTP_204_NO_CONTENT)
                else:
                    if commentData[0].UID.UID == userID:
                        commentData.delete()
                        return JsonResponse({'success':True, 'result':"댓글 삭제 완료", 'errorMessage':""},status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"해당 유저의 댓글이 아닙니다."}, safe=False, status=status.HTTP_403_FORBIDDEN)



@swagger_auto_schema(
    method='put',  
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
       request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'title': openapi.Schema('글 제목', type=openapi.TYPE_STRING),
                    'contents': openapi.Schema('글 내용', type=openapi.TYPE_STRING),        
                    'TBID': openapi.Schema('책 TBID', type=openapi.TYPE_INTEGER),
                    'PID': openapi.Schema('책 BID', type=openapi.TYPE_INTEGER),
        },
        required=['title','contents','PID']
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


@api_view(['PUT'])
def modifyCommunityPost(request,slug):
    exceptDict = None   
    if request.headers.get('access_token') is None:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"형식이 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        userID = checkAuth_decodeToken(request)
        if userID == -1:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
        elif userID == -2:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_401_UNAUTHORIZED)
        else:                            
            if (request.method == 'PUT'):
                data = JSONParser().parse(request)
                # userID = UID
                userData = User.objects.filter(UID = userID)
                if slug =="0":
                    postData = AnyCommunity.objects.filter(APID = data['PID'])
                
                elif slug =="1":
                    postData = MarketCommunity.objects.filter(MPID = data['PID'])

                elif slug =="2":
                    postData = QnACommunity.objects.filter(QPID = data['PID'])

                if len(userData) != 0 and postData[0].UID.UID == userID:
                    data['UID']=userData[0].UID
                    data['updateAt']=str(datetime.datetime.utcnow())
                    if slug == "0":
                        postSerializer = AnyCommunityDetailSerializer(postData[0],data = data)

                    elif slug == "1":
                        postSerializer = MarketCommunityDetailSerializer(postData[0],data = data)

                    elif slug == "2":
                        postSerializer = QnACommunityDetailSerializer(postData[0],data = data)

                    if postSerializer.is_valid():
                        postSerializer.save()
                        return JsonResponse({
                        'success':True,
                        'result' :"게시글 수정 완료",
                        'errorMessage':""
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

def like_checkHot(flag,PID):
    tempList = list()
    if PID is not None:
        if flag == 0: #자게
            queryData = AnyCommunity.objects.get(APID = PID)

        elif flag == 1 : # 중고장터
             queryData = MarketCommunity.objects.get(MPID = PID)

        elif flag == 2 : #QNA
            queryData = QnACommunity.objects.get(QPID = PID)

        if queryData is not None: 
            if isHot(queryData):
                hotCommunity_injector(flag, queryData)
                return True
            else:
                return False
        else :
            return False
    else : 
        return False

def isHot(queryData): #10개가 넘으면 True 반환
    if len(queryData.like) >= 10:
        return True
    else:
        return False
def hotCommunity_injector(flag, instance): #핫게시판에 injection하는 함수
    if flag == 0: #자게
        if len(HotCommunity.objects.filter(APID=instance.APID)) == 0:
            query = HotCommunity(
                APID = instance,
                communityType = 0
            )
            query.save()
    elif flag == 1: # 중고장터
        if len(HotCommunity.objects.filter(MPID=instance.MPID)) == 0:
            query = HotCommunity(
                MPID = instance,
                communityType = 1
            )
            query.save()
    elif flag == 2: #QNA
        if len(HotCommunity.objects.filter(QPID=instance.QPID)) == 0:
            query = HotCommunity(
                QPID = instance,
                communityType = 2
            )
            query.save()

def likeFunction(queryData,UID): #좋아요 쿼리 등록
    temp = queryData.like
    if temp.count(UID) == 0:
        queryData.like = temp + [UID]
        queryData.save()
        return True
    else:
        temp.remove(UID)
        queryData.like = temp
        queryData.save()
        return False


@swagger_auto_schema(
    method='post',
    operation_description= "pk1 => 0 = '자유게시판', 1 = '장터게시판', 2 = 'QnA게시판', 3 = 'HOT게시판' , pk2 => PID",
    manual_parameters=[
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
                        'isLiked' : openapi.Schema('좋아요중인지?', type=openapi.TYPE_BOOLEAN)
                    }
                ),
                'errorMessage':openapi.Schema('에러메시지', type=openapi.TYPE_STRING),
            }
        )
    }
)
@api_view(['POST'])
def communityLike(request,pk1,pk2):
    flag = checkAuth_decodeToken(request)
    print(pk1, pk2)
    # exceptDict = {'BID' : 0, 'UID':0}
    exceptDict = None
    if flag == 0:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    elif flag == -1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == -2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        temp = list()
        if pk1 == 0: #자게
            queryData = AnyCommunity.objects.get(APID = pk2)
        elif pk1 == 1: #장터
            queryData = MarketCommunity.objects.get(MPID = pk2)
        elif pk1 == 2: # QnA
            queryData = QnACommunity.objects.get(QPID = pk2)
        elif pk1 == 3: #핫게
            hotQuery = HotCommunity.objects.get(HPID = pk2)
            isLiked = False
            if hotQuery.APID is not None: #자게
                queryData = AnyCommunity.objects.get(APID= hotQuery.APID.APID)
                isLiked = likeFunction(queryData,flag)
            elif hotQuery.MPID is not None: #장터
                queryData = MarketCommunity.objects.get(MPID= hotQuery.MPID.MPID)
                isLiked = likeFunction(queryData,flag)
            elif hotQuery.QPID is not None: # QnA
                queryData = QnACommunity.objects.get(QPID= hotQuery.QPID.QPID)
                isLiked = likeFunction(queryData,flag)
            return JsonResponse({'success':True, 'result':{'isLiked':isLiked}, 'errorMessage':""}, status = status.HTTP_200_OK)
        if queryData is not None:
            if likeFunction(queryData, flag):
                like_checkHot(pk1, pk2)
                return JsonResponse({'success':True, 'result':{'isLiked':True}, 'errorMessage':""}, status = status.HTTP_200_OK)
            else:
                return JsonResponse({'success':True, 'result':{'isLiked':False}, 'errorMessage':""}, status = status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"해당 PID의 게시글이 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"해당 호출은 지원하지 않습니다."}, status = status.HTTP_405_Method_Not_Allowed)

@api_view(['GET'])
def getHotCommunity(request):
    if request.method == 'GET':
        CommunityQuery = HotCommunity.objects.order_by('-createAt')
        quantity = 20 #기본 quntity 값은 20개
        startpagination = 0 #기본 startpagination 값은 0
        endpagination = quantity #기본 endpagination 값은 qunatity값과 동일, page 값이 들어오면 pagination 지원
        Posts = CommunityQuery.all()
        total_size = len(Posts)
        if request.GET.get('quantity') is not None: #URL에 'quantity' Query가 들어있으면 값 입력
            quantity = int(request.GET.get('quantity')) 

        if request.GET.get('page') is not None: #URL에 'page' Query가 들어있으면 값 입력
            startpagination = (int(request.GET.get('page')) - 1) * quantity
            endpagination = int(request.GET.get('page')) * quantity

        if startpagination > len(Posts):
            startpagination = len(Posts)

        if endpagination > len(Posts):
            endpagination = len(Posts)

        Posts = Posts[startpagination : endpagination]
        communityList = list()

        for i in Posts:
            if i.communityType == 0:
                tempID = i.APID.APID
                anyQuery = AnyCommunity.objects.filter(APID = tempID)
                tempList = AnyCommunitySerializer(anyQuery, many=True)
                tempQuery = tempList.data
                del tempQuery[0]['APID']
                tempQuery[0]['commentCnt']=len(AnyComment.objects.filter(APID = tempID))
                communityList.append(dictionaryInjector(tempQuery[0], i, tempID))
            if i.communityType == 1:
                tempID = i.MPID.MPID
                anyQuery = MarketCommunity.objects.filter(MPID = tempID)
                tempList = MarketCommunitySerializer(anyQuery, many=True)
                tempQuery = tempList.data
                del tempQuery[0]['MPID']
                tempQuery[0]['commentCnt']=len(MarketComment.objects.filter(MPID = tempID))
                communityList.append(dictionaryInjector(tempQuery[0], i, tempID))
            if i.communityType == 2: #Todo QnA에 추가되는거 생각해보자
                tempID = i.QPID.QPID
                anyQuery = QnACommunity.objects.filter(QPID = tempID)
                tempList = QnACommunitySerializer(anyQuery, many=True)
                tempQuery = tempList.data
                del tempQuery[0]['QPID']
                tempQuery[0]['commentCnt']=len(QnAComment.objects.filter(QPID = tempID))
                communityList.append(dictionaryInjector(tempQuery[0], i, tempID))
        return JsonResponse({
            'success':True,
            'result' :{'postList':communityList, 'total_size':len(communityList)}, 
            'errorMessage':""
            }, 
            status=status.HTTP_200_OK)
def dictionaryInjector(data, query, itemID):
    data['PID'] = itemID
    data['parentQPID'] = 0
    data['communityType'] = query.communityType
    data['likeCnt']=len(data['like'])
    del data['like']
    return data
                  # tempQuery[0]['PID'] = tempID 
                # tempQuery[0]['parentQPID'] = 0
                # tempQuery[0]['communityType'] = i.communityType
                # tempQuery[0]['likeCnt']=len(Posts[i].like)
                # del tempQuery[0]['like']
