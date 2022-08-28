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
from bookky.serializers.bookserializers import *
from bookky.auth.auth import authValidation
from bookky.views.uploadView import decodeBase64
from bookky.views.pushsystem import send_push_alert, PushMessageObject
from django.db.models import Q
from django.db import connection

from urllib import parse
import requests
import datetime
import urllib.request
import json
import time
import datetime
import base64
import os
import shutil

@swagger_auto_schema(
    method='get',
    operation_description= "slug => 0 = '자유게시판', 1 = '장터게시판', 2 = 'QnA게시판', 3 = '내글보기'",
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
                            'likeCnt':openapi.Schema('좋아요 수', type=openapi.TYPE_INTEGER),
                            'replyCnt':openapi.Schema('답글 수', type=openapi.TYPE_INTEGER)
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
            if slug == "0":        # 쿼리에서 createAt 으로 정렬 후 ? updateAt은? updateAt으로 해야겟네
                CommunityQuery = AnyCommunity.objects.order_by('-updateAt')
            elif slug == "1":
                CommunityQuery = MarketCommunity.objects.order_by('-updateAt')
            elif slug == "2":
                CommunityQuery = QnACommunity.objects.filter(parentQPID = 0).order_by('-updateAt')
            elif slug == "3":
                flag = checkAuth_decodeToken(request)
                exceptDict = None
                if flag == 0:
                    return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
                elif flag == -1:
                    return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
                elif flag == -2:
                    return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)

                Any = AnyCommunity.objects.filter(UID = flag).order_by('-updateAt')
                Mar = MarketCommunity.objects.filter(UID = flag).order_by('-updateAt')
                QnA = QnACommunity.objects.filter(parentQPID = 0).filter(UID = flag).order_by('-updateAt')

                mypostCnt = len(Any) + len(Mar) + len(QnA)
                mypost = list()
                            
                AnySer = AnyCommunitySerializer(Any,many=True)
                MarSer = MarketCommunitySerializer(Mar,many=True)
                QnASer = QnACommunitySerializer(QnA,many=True)
    
                for i in range(len(Any)):
                    AnySer.data[i]['likeCnt'] = len(AnySer.data[i]['like'])
                    AnySer.data[i]['commentCnt'] = len(AnyComment.objects.filter(APID = AnySer.data[i]['APID']))
                    del AnySer.data[i]['like']
                    #del AnySer.data[i]['contents']
                    AnySer.data[i]['PID'] = AnySer.data[i]['APID']
                    del AnySer.data[i]['APID']
                    AnySer.data[i]['updateAt'] = Any[i].updateAt
                    AnySer.data[i]['replyCnt'] = -1
                    AnySer.data[i]['communityType'] = 0

                for i in range(len(Mar)):
                    MarSer.data[i]['likeCnt'] = len(MarSer.data[i]['like'])
                    MarSer.data[i]['commentCnt'] = len(MarketComment.objects.filter(MPID = MarSer.data[i]['MPID']))
                    del MarSer.data[i]['like']
                    #del MarSer.data[i]['contents']
                    MarSer.data[i]['PID'] = MarSer.data[i]['MPID']
                    del MarSer.data[i]['MPID']
                    MarSer.data[i]['updateAt'] = Mar[i].updateAt
                    MarSer.data[i]['replyCnt'] = -1
                    MarSer.data[i]['communityType'] = 1

                for i in range(len(QnA)):
                    QnASer.data[i]['likeCnt'] = len(QnASer.data[i]['like'])
                    QnASer.data[i]['commentCnt'] = len(QnAComment.objects.filter(QPID = QnASer.data[i]['QPID']))
                    del QnASer.data[i]['like']
                    #del QnASer.data[i]['contents']
                    del QnASer.data[i]['parentQPID']
                    QnASer.data[i]['PID'] = QnASer.data[i]['QPID']
                    replyCnt = len(QnACommunity.objects.filter(parentQPID = QnASer.data[i]['QPID']))
                    del QnASer.data[i]['QPID']
                    QnASer.data[i]['updateAt'] = QnA[i].updateAt
                    QnASer.data[i]['replyCnt'] = replyCnt
                    QnASer.data[i]['communityType'] = 2


                postdata = (AnySer.data + MarSer.data + QnASer.data)
                postdata = sorted(postdata,key=lambda x:x['updateAt'], reverse = True)
                for i in postdata:
                    del i["updateAt"]

                #print(postdata)
                # Any , Mar , QnA   =>   title, PID, updateAt 만 나옴.  하나의 배열로 만들어서 updateAt으로 정렬 후 communityType 넣어주고 return
                
                return JsonResponse({
                    'success':True,
                    'result' :{'postList':postdata, 'total_size':mypostCnt}, 
                    'errorMessage':""
                }, 
                status=status.HTTP_200_OK)
        
        except TempBook.DoesNotExist:
                return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"해당 Community에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"}, status=status.HTTP_404_NOT_FOUND)
                
                #Any = AnyCommunity.objects.filter( = 0).order_by('-updateAt')


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
        elif slug == "2":
            serializer = QnACommunitySerializer(Posts,many=True)

        userData = []
        subData = []

        for i in range(len(Posts)):
            if slug == "0":
                serializer.data[i]['commentCnt']=len(AnyComment.objects.filter(APID = Posts[i].APID))
            elif slug == "1":
                serializer.data[i]['commentCnt']=len(MarketComment.objects.filter(MPID = Posts[i].MPID))
            elif slug == "2":
                serializer.data[i]['commentCnt']=len(QnAComment.objects.filter(QPID = Posts[i].QPID))
                serializer.data[i]['replyCnt']=len(QnACommunity.objects.filter(parentQPID = Posts[i].QPID))


            serializer.data[i]['likeCnt']=len(Posts[i].like)
            del serializer.data[i]['like']


            if slug == "0":
                serializer.data[i]['PID'] = serializer.data[i]['APID']
                del serializer.data[i]['APID']            
            elif slug == "1":
                serializer.data[i]['PID'] = serializer.data[i]['MPID']
                del serializer.data[i]['MPID']
            elif slug == "2":
                serializer.data[i]['PID'] = serializer.data[i]['QPID']
                del serializer.data[i]['QPID']
            

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
        openapi.Parameter('access-token', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='회원이라면 토큰 넣고 비회원이면 넣지 않는다.'),
        openapi.Parameter('mode', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='(iOS==1)')
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
                            'isAccessible':openapi.Schema('접근 가능', type=openapi.TYPE_BOOLEAN),
                            'TBID':openapi.Schema('책 BID', type=openapi.TYPE_STRING)
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
    print(request.headers.get('access_token',None))
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
            

            elif slug1 == "2":
                PostData = QnACommunity.objects.filter(QPID = slug2)
                serializer = QnACommunityDetailSerializer(PostData,many=True)
                replyData = QnACommunity.objects.filter(parentQPID = slug2)
                commentData = QnAComment.objects.filter(QPID = PostData[0].QPID).order_by('updateAt')
                commentserializer = QnACommentSerializer(commentData,many=True)
            else:
                return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"잘못된 slug 입니다."}, status=status.HTTP_404_NOT_FOUND)

        except TempBook.DoesNotExist:
            return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"해당 Community에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"}, status=status.HTTP_404_NOT_FOUND)

        postuserData = []
        RcommentData = list()
        commentCnt= len(commentData)
        if (int(flag) in serializer.data[0]['like']) == True:
            serializer.data[0]["isLiked"]=True
        else:
            serializer.data[0]["isLiked"]=False
        
        if slug1 != "2":    

            # 댓글 데이터 가공
            k = 0
            for i in commentserializer.data:
                if (int(flag) in i['like']) == True:
                    i["isLiked"]=True
                else:
                    i["isLiked"]=False
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
                    i["updateAt"] = datetime.datetime.strptime(i["updateAt"], '%Y-%m-%dT%H:%M:%S.%f').strftime("%Y-%m-%d %H:%M")
                    
                    RcommentData.append(i)
                k = k + 1
            
            for i in commentserializer.data:
                if i["parentID"] != 0:
                    for j in RcommentData:
                        if i["parentID"] == j["CID"]:
                            #del i["parentID"]
                            del i["UID"]
                            i["updateAt"] = datetime.datetime.strptime(i["updateAt"], '%Y-%m-%dT%H:%M:%S.%f').strftime("%Y-%m-%d %H:%M")
                            j["childComment"].append(i)
                            break
                
            
            for i in RcommentData:
                #del i["parentID"]
                del i["UID"]
            
            # ios 1차원 데이터 작업
            if request.GET.get('mode') is not None and request.GET.get('mode') == "1":
                RcommentData2 = list()
                
                for i in RcommentData:
                    temp = i.copy()
                    del temp["childComment"]
                    temp["reply"]=0
                    RcommentData2.append(temp)
                    
                    if 'childComment' in i:
                        for j in i["childComment"]:
                            j["reply"]=1
                            RcommentData2.append(j)

                RcommentData = RcommentData2

        

        #post 정보
        BookSer = dict()
        serializer.data[0]['nickname']=PostData[0].UID.nickname
        serializer.data[0]['thumbnail']=PostData[0].UID.thumbnail
        serializer.data[0]["updateAt"] = datetime.datetime.strptime(serializer.data[0]["updateAt"], '%Y-%m-%dT%H:%M:%S.%f').strftime("%Y-%m-%d %H:%M")
        serializer.data[0]["createAt"] = datetime.datetime.strptime(serializer.data[0]["createAt"], '%Y-%m-%dT%H:%M:%S.%f').strftime("%Y-%m-%d %H:%M")

        if serializer.data[0]['UID'] == flag:
            serializer.data[0]['isAccessible'] = True
        else:
            serializer.data[0]['isAccessible'] = False
        del serializer.data[0]['UID']
        
        #책 정보
        if PostData[0].TBID_id is None:
            serializer.data[0]['TBID'] = 0
        else:
            serializer.data[0]['TBID'] = PostData[0].TBID_id
            Book = TempBook.objects.filter(TBID = PostData[0].TBID_id)
            BookSer = BookSearchSerializer(Book,many=True).data[0]
            
            del BookSer['BOOK_INTRODUCTION']
            del BookSer['PUBLISH_DATE']
            

        if slug1 != "2":
            return JsonResponse({
                'success':True,
                'result' :{'postdata':serializer.data[0],'commentdata':RcommentData, 'commentCnt':commentCnt, 'Book':BookSer},
                'errorMessage':""
            },status=status.HTTP_200_OK)

        else:
            
            postuserData = []
            replyCnt= len(replyData)

            replyAlldata = list()
            k=0
            
            serializer1 = QnACommunityDetailSerializer(replyData,many=True)
            for k in range(replyCnt):
                
                serializer1.data[k]['nickname']=replyData[k].UID.nickname
                serializer1.data[k]['thumbnail']=replyData[k].UID.thumbnail
                serializer1.data[k]['PID']=replyData[k].QPID
                serializer1.data[k]['commentCnt']=len(QnAComment.objects.filter(QPID = replyData[k].QPID))
                serializer1.data[k]["updateAt"] = datetime.datetime.strptime(serializer1.data[k]["updateAt"], '%Y-%m-%dT%H:%M:%S.%f').strftime("%Y-%m-%d %H:%M")
                if (int(flag) in serializer1.data[k]['like']) == True:
                    serializer1.data[k]["isLiked"]=True
                else:
                    serializer1.data[k]["isLiked"]=False

                if serializer1.data[k]['UID'] == flag:
                    serializer1.data[k]['isAccessible'] = True
                else:
                    serializer1.data[k]['isAccessible'] = False
                del serializer1.data[k]['UID']
        
                #책 정보
                if replyData[k].TBID_id is None:
                    serializer1.data[k]['TBID'] = 0
                    serializer1.data[k]['Book'] = dict()
                else:
                    serializer1.data[k]['TBID'] = replyData[k].TBID_id
                    Book = TempBook.objects.filter(TBID = replyData[k].TBID_id)
                    serializer1.data[k]['Book'] = BookSearchSerializer(Book,many=True).data[0]
                    del serializer1.data[k]['Book']['BOOK_INTRODUCTION']
                    del serializer1.data[k]['Book']['PUBLISH_DATE']



                replyAlldata.append(serializer1.data[k])

            return JsonResponse({
                'success':True,
                'result' :{'postdata':serializer.data[0],'replydata':replyAlldata, 'commentCnt':commentCnt, 'replyCnt':replyCnt, 'Book':BookSer},
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
                    'parentQPID': openapi.Schema('답글 QPID', type=openapi.TYPE_INTEGER),
                    'Images':openapi.Schema('태그이름', type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING))
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

                    if data['TBID'] == 0:
                        del data['TBID']
                    else:
                        tempTBID = TempBook.objects.get(TBID = int(data['TBID']))
                        data['TBID'] = tempTBID.TBID

                    #print(data['UID'])
                    #print(data['title'])
                    #print(data['Images'])

                    if data['Images'] is not None:
                        imageArray = data['Images']
                        del data['Images']

                    if slug == "0":
                        del data['parentQPID']
                        postSerializer = AnyCommunityDetailSerializer(data = data)

                    elif slug == "1":
                        del data['parentQPID']
                        postSerializer = MarketCommunityDetailSerializer(data = data)

                    elif slug == "2":
                        postSerializer = QnACommunityDetailSerializer(data = data)

                    if postSerializer.is_valid():
                        #print(settings.MEDIA_ROOT+'/thumbnail/AnyCommunity/')
                        #print(data['createAt'])
                        Post = postSerializer.save()
                        if slug == "0":
                            PID = Post.APID
                            Path = settings.MEDIA_ROOT+'/thumbnail/AnyCommunity/'+str(PID)+'/'
                        elif slug == "1":
                            PID = Post.MPID
                            Path = settings.MEDIA_ROOT+'/thumbnail/MarketCommunity/'+str(PID)+'/'
                        elif slug == "2":
                            PID = Post.QPID
                            Path = settings.MEDIA_ROOT+'/thumbnail/QnACommunity/'+str(PID)+'/'
                    else:
                        return JsonResponse({
                        'success':False,
                        'result' :{},
                        'errorMessage':postSerializer.errors
                        })


                    # save 이후
                    
                     # encodedImage
                    if len(imageArray)==0 or imageArray[0].find(';') == -1:
                        return JsonResponse({
                            'success':True,
                            'result' :"글 작성 완료",
                            'errorMessage':""
                            },status=status.HTTP_201_CREATED)
                    else:
                        
                        try:
                        #     # for image_string in self.context.get("images"):
                            num = 1
                            tempfilenames = list()
                            for Image in imageArray:

                                if len(Image) ==0 or Image.find(';') == -1:
                                    continue
                                #Image = imagedata
                                header, Data = Image.split(';base64,') #base64형태는 data:image/png;base64,로 시작함 즉 파일 형태와 파일 확장자가 앞에 붙음 이걸 이미지로 디코딩하면 깨져버리기 때문에 분할 해줘야함
                                data_format, ext = header.split('/') #data타입과 확장자 분리함
                                image_data = base64.b64decode(Data)
                                imagesname = str(num) + "." + ext
                                
                                if not os.path.exists(Path):
                                    os.makedirs(Path)
                            
                                with open(Path+imagesname, 'wb') as f:
                                    f.write(image_data)
                                
                                tempfilenames.append("http://203.255.3.144:8010" + Path[29:] + imagesname)

                                num += 1
                                    # num += 1
                                    # imageArray.append(image_data)
                    
                        except TypeError:
                            return JsonResponse({
                            'success':False,
                            'result' :{},
                            'errorMessage':"이미지 저장 실패"
                            })
                            
                        #이미지 경로 설정 = 경로,경로,경로 -> string 형태
                        data['postImage'] = tempfilenames 


                        if slug == "0":
                            postData = AnyCommunity.objects.filter(APID = PID)
                            postSerializer = AnyCommunityDetailSerializer(postData[0],data = data)

                        elif slug == "1":
                            postData = MarketCommunity.objects.filter(MPID = PID)
                            postSerializer = MarketCommunityDetailSerializer(postData[0],data = data)

                        elif slug == "2":
                            postData = QnACommunity.objects.filter(QPID = PID)
                            postSerializer = QnACommunityDetailSerializer(postData[0],data = data)

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
                                'errorMessage': postSerializer.errors
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
                    token = ""
                    data['UID']=userData[0].UID
                    data['createAt']=str(datetime.datetime.utcnow())
                    del data['PID']
                    if slug == "0":
                        data['APID']=postData[0].APID
                        postSerializer = AnyCommentSerializer(data = data)
                        postQuery = AnyCommunity.objects.get(APID = data['APID'])
                    elif slug == "1":
                        data['MPID']=postData[0].MPID
                        postSerializer = MarketCommentSerializer(data = data)
                        postQuery = MarketCommunity.objects.get(MPID = data['MPID'])
                    elif slug == "2":
                        data['QPID']=postData[0].QPID
                        postSerializer = QnACommentSerializer(data = data)
                        postQuery = QnACommunity.objects.get(QPID = data['QPID'])

                    if postSerializer.is_valid():
                        postman_id = find_post_master(postQuery)
                        messageObject = PushMessageObject(str(postQuery.title) , data['comment'])
                        send_push_alert(postman_id, messageObject)
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


def find_post_master(objects):
    postMasterQuery = objects.UID.UID
    print(postMasterQuery)
    postMasterToken = objects.UID.pushToken
    print(postMasterToken)
    #UserQuery = User.objects.UID
    return postMasterQuery

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
def deleteCommunityPost(request,slug):
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
                    Path = settings.MEDIA_ROOT+'/thumbnail/AnyCommunity/'+str(data['PID'])+'/'
                elif slug == "1":
                    postData = MarketCommunity.objects.filter(MPID = data['PID'])
                    Path = settings.MEDIA_ROOT+'/thumbnail/MarketCommunity/'+str(data['PID'])+'/'
                elif slug == "2":
                    postData = QnACommunity.objects.filter(QPID = data['PID'])
                    Path = settings.MEDIA_ROOT+'/thumbnail/QnACommunity/'+str(data['PID'])+'/'
                else:
                    return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"잘못된 slug"}, safe=False, status=status.HTTP_400_BAD_REQUEST)

                if len(postData) == 0 :
                    return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"해당 포스트의 정보 없음"}, safe=False, status=status.HTTP_204_NO_CONTENT)
                else:
                    if postData[0].UID.UID == userID:                    
                        if os.path.exists(Path):
                            shutil.rmtree(Path)
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
def deleteCommunityComment(request,slug):
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
                    commentData = QnAComment.objects.filter(QCID = data['CID'])
                else:
                    return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"잘못된 slug"}, safe=False, status=status.HTTP_400_BAD_REQUEST)

                if len(commentData) == 0 :
                    return JsonResponse({'success':False,'result': exceptDict, 'errorMessage':"해당 포스트의 정보 없음"}, safe=False, status=status.HTTP_204_NO_CONTENT)
                else:
                    if commentData[0].UID.UID == userID:

                        if commentData[0].parentID == 0: # 댓글인 경우
                            print(data['CID'])
                            if slug == "0":
                                childData = AnyComment.objects.filter(parentID = data['CID'])
                            elif slug == "1":
                                childData = MarketComment.objects.filter(parentID = data['CID'])
                            elif slug == "2":
                                childData = QnAComment.objects.filter(parentID = data['CID'])

                            if(len(childData) == 0): # 대댓글이 없다면
                                commentData.delete()

                            else: # 대댓글이 있다면
                                data["parentID"] = 0
                                data["UID"] = 0
                                data["comment"] = "삭제된 댓글입니다."
                                #data["like"] = {}
                                #data["updateAt"] = str(datetime.datetime.utcnow())                                    
                                if slug == "0":
                                    data["APID"] = commentData[0].APID.APID
                                    commentSerializer = AnyCommentSerializer(commentData[0],data = data)
                                elif slug == "1":
                                    data["MPID"] = commentData[0].MPID.MPID
                                    commentSerializer = MarketCommentSerializer(commentData[0],data = data)
                                elif slug == "2":
                                    data["QPID"] = commentData[0].QPID.QPID
                                    commentSerializer = QnACommentSerializer(commentData[0],data = data)

                                
                                if commentSerializer.is_valid():
                                    
                                    commentSerializer.save()
                                    return JsonResponse({
                                        'success':True,
                                        'result' :"대댓글 삭제 완료",
                                        'errorMessage':""
                                    })
                                else:
                                    return JsonResponse({
                                        'success':False,
                                        'result' :"대댓글 삭제 실패",
                                        'errorMessage':commentSerializer.errors
                                    })
                        else: # 대댓글인 경우
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
                    'Images':openapi.Schema('이미지', type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING))
        },
        required=['title','contents','PID','Images']
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
                imageArray = data['Images']
                del data['Images']

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
                        Path = settings.MEDIA_ROOT+'/thumbnail/AnyCommunity/'+str(data['PID'])+'/'
                        TYPE = '"bookky_anycommunity"'
                        TYPEPID = '"APID"'

                    elif slug == "1":
                        postSerializer = MarketCommunityDetailSerializer(postData[0],data = data)
                        Path = settings.MEDIA_ROOT+'/thumbnail/MarketCommunity/'+str(data['PID'])+'/'
                        TYPE = '"bookky_marketcommunity"'
                        TYPEPID = '"MPID"'

                    elif slug == "2":
                        data['parentQPID'] = postData[0].parentQPID
                        postSerializer = QnACommunityDetailSerializer(postData[0],data = data)
                        Path = settings.MEDIA_ROOT+'/thumbnail/QnACommunity/'+str(data['PID'])+'/'
                        TYPE = '"bookky_qnacommunity"'
                        TYPEPID = '"QPID"'

                    if data['TBID'] == 0:
                        data['TBID']=None
                                          
                    if len(postData[0].postImage) !=0 or (len(imageArray)!=0 and imageArray[0].find(';') != -1):
                        # 이미지가 있거나                   들어온 이미지가 있고    형식도 맞으면! 
                        try:
                        #     # for image_string in self.context.get("images"):
                            num = 1
                            tempfilenames = list()
                            # 이미지가 기존에 있는 경우는 고려하지 않음.

                            #if os.path.exists(Path):
                                #shutil.rmtree(Path)
                            #우선 해당 영역을 지운 뒤, 생각!

                            for Image in imageArray:
                                
                                if len(Image) == 0 or Image.find(';') == -1:
                                    continue

                                #Image = imagedata
                                header, Data = Image.split(';base64,') #base64형태는 data:image/png;base64,로 시작함 즉 파일 형태와 파일 확장자가 앞에 붙음 이걸 이미지로 디코딩하면 깨져버리기 때문에 분할 해줘야함
                                data_format, ext = header.split('/') #data타입과 확장자 분리함
                                image_data = base64.b64decode(Data)
                                #image_root = settings.MEDIA_ROOT+'/thumbnail/' + path + "thumbnail" + "." + ext
                                imagesname = str(num) + "." + ext
                                
                                if not os.path.exists(Path):
                                    os.makedirs(Path)
                            
                                with open(Path+imagesname, 'wb') as f:
                                    f.write(image_data)
                                
                                tempfilenames.append("http://203.255.3.144:8010" + Path[29:] + imagesname)

                                num += 1
                                    # num += 1
                                    # imageArray.append(image_data)
                    
                        except TypeError:
                            return JsonResponse({
                            'success':False,
                            'result' :{},
                            'errorMessage':"이미지 저장 실패"
                            })
                            
                        #이미지 경로 설정 = 경로,경로,경로 -> string 형태
                        
                        data['postImage'] = tempfilenames
                        
                        if len(tempfilenames) == 0: # 빈 배열 이슈 해결 해야함.
                            postData[0].postImage.clear()
                            data['postImage'] = []
                            #postData[0].save()
                            #print("@")

                        


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
    if len(queryData.like) >= 3:
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

@swagger_auto_schema(
    method='get',
    operation_description= "핫게시판",
    manual_parameters=[
        openapi.Parameter('quantity',openapi.IN_QUERY,type=openapi.TYPE_INTEGER, description='원하는 수량'),
        openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='원하는 페이지'),
        openapi.Parameter('access-token', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='회원이라면 토큰 넣고 비회원이면 넣지 않는다.')
    ],
)
@api_view(['GET'])
def getHotCommunity(request):
    if request.method == 'GET':
        CommunityQuery = HotCommunity.objects.order_by('-updateAt')
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
                tempQuery[0]['replyCnt']=-1
                communityList.append(dictionaryInjector(tempQuery[0], i, tempID))
            if i.communityType == 1:
                tempID = i.MPID.MPID
                anyQuery = MarketCommunity.objects.filter(MPID = tempID)
                tempList = MarketCommunitySerializer(anyQuery, many=True)
                tempQuery = tempList.data
                del tempQuery[0]['MPID']
                tempQuery[0]['commentCnt']=len(MarketComment.objects.filter(MPID = tempID))
                tempQuery[0]['replyCnt']=-1
                communityList.append(dictionaryInjector(tempQuery[0], i, tempID))
            if i.communityType == 2: #Todo QnA에 추가되는거 생각해보자
                tempID = i.QPID.QPID
                anyQuery = QnACommunity.objects.filter(QPID = tempID)
                tempList = QnACommunitySerializer(anyQuery, many=True)
                tempQuery = tempList.data
                del tempQuery[0]['QPID']
                tempQuery[0]['commentCnt']=len(QnAComment.objects.filter(QPID = tempID))
                tempQuery[0]['replyCnt']=len(QnACommunity.objects.filter(parentQPID = tempID))
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





@swagger_auto_schema(
    method='get',
    operation_description= "게시판 최상위 6개의 게시글을 response",
    manual_parameters=[
        openapi.Parameter('access-token', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='회원이라면 토큰 넣고 비회원이면 넣지 않는다.'),
        openapi.Parameter('count', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='원하는 개수'),
    ],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'a' : openapi.Schema('결과', type=openapi.TYPE_STRING)
                    }
                ),
                'errorMessage':openapi.Schema('에러메시지', type=openapi.TYPE_STRING),
            }
        )
    }
)

@api_view(['GET'])
def getCommunityHome(request):
    if request.method == 'GET':
        count = 6
        if request.GET.get('count') is not None:
            count = int(request.GET.get('count'))

        Hot,Any,Mar,QnA = CommunityCount(count)
        
        return JsonResponse({
            'success':True,
            'result' :{'HotList':Hot,'AnyList':Any,'MarketList':Mar,'QnAList':QnA},
            'errorMessage':""
            },            status=status.HTTP_200_OK) 

    else :
        return JsonResponse({
            'success':False,
            'result' :{},
            'errorMessage':"GET이 아님"
            })


def CommunityCount(count):
    Hot = HotCommunity.objects.order_by('-updateAt')[:count]
    Any = AnyCommunity.objects.order_by('-updateAt')[:count]
    Mar = MarketCommunity.objects.order_by('-updateAt')[:count]
    QnA = QnACommunity.objects.filter(parentQPID = 0).order_by('-updateAt')[:count]
    
    
    
    AnySer = AnyCommunitySerializer(Any,many=True)
    MarSer = MarketCommunitySerializer(Mar,many=True)
    QnASer = QnACommunitySerializer(QnA,many=True)
    
    for i in range(len(Any)):
        del AnySer.data[i]['like']
        del AnySer.data[i]['contents']
        AnySer.data[i]['PID'] = AnySer.data[i]['APID']
        del AnySer.data[i]['APID']

    for i in range(len(Mar)):
        del MarSer.data[i]['like']
        del MarSer.data[i]['contents']
        MarSer.data[i]['PID'] = MarSer.data[i]['MPID']
        del MarSer.data[i]['MPID']

    for i in range(len(QnA)):
        del QnASer.data[i]['like']
        del QnASer.data[i]['contents']
        del QnASer.data[i]['parentQPID']
        QnASer.data[i]['PID'] = QnASer.data[i]['QPID']
        del QnASer.data[i]['QPID']


    HotSer = list()
    for i in Hot:
        if i.communityType == 0:
            tempQuery = AnyCommunitySerializer(AnyCommunity.objects.filter(APID = i.APID.APID), many=True).data
            tempQuery[0]['PID'] = tempQuery[0]['APID']
            tempQuery[0]['communityType'] = 0
            del tempQuery[0]['APID']

        elif i.communityType == 1:
            tempQuery = MarketCommunitySerializer(MarketCommunity.objects.filter(MPID = i.MPID.MPID), many=True).data
            tempQuery[0]['PID'] = tempQuery[0]['MPID']
            tempQuery[0]['communityType'] = 1
            del tempQuery[0]['MPID']

        elif i.communityType == 2:
            tempQuery = QnACommunitySerializer(QnACommunity.objects.filter(QPID = i.QPID.QPID), many=True).data
            tempQuery[0]['PID'] = tempQuery[0]['QPID']
            tempQuery[0]['communityType'] = 2
            del tempQuery[0]['QPID']
            del tempQuery[0]['parentQPID']

        del tempQuery[0]['like']
        del tempQuery[0]['contents']
        HotSer.append(tempQuery[0])

    return HotSer, AnySer.data, MarSer.data, QnASer.data





@swagger_auto_schema(
    method='get',
    operation_description= "slug1 => 0 = '자유게시판', 1 = '장터게시판', 2 = 'QnA게시판'  , slug2 => PID",
    manual_parameters=[
        openapi.Parameter('access-token', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='회원이라면 토큰 넣고 비회원이면 넣지 않는다.'),
        openapi.Parameter('mode', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='(iOS==1)')
    ],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'commentdata' : openapi.Schema('댓글정보', type=openapi.TYPE_STRING),
                        'commentCnt' : openapi.Schema('댓글갯수', type=openapi.TYPE_INTEGER)
                    }
                ),
                'errorMessage':openapi.Schema('에러메시지', type=openapi.TYPE_STRING),
            }
        )
    }
)
@api_view(['GET']) #우석 이거 왜 POST호출이야?

def getCommunityComment(request,slug1,slug2):

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
                commentData = AnyComment.objects.filter(APID = slug2).order_by('updateAt')
                commentserializer = AnyCommentSerializer(commentData,many=True)

            elif slug1 == "1":
                commentData = MarketComment.objects.filter(MPID = slug2).order_by('updateAt')
                commentserializer = MarketCommentSerializer(commentData,many=True)     

            elif slug1 == "2":
                commentData = QnAComment.objects.filter(QPID = slug2).order_by('updateAt')
                commentserializer = QnACommentSerializer(commentData,many=True)
            else:
                return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"잘못된 slug 입니다."}, status=status.HTTP_404_NOT_FOUND)

        except TempBook.DoesNotExist:
            return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"해당 Community에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"}, status=status.HTTP_404_NOT_FOUND)

    # AT 넣기

        RcommentData = list()
        commentCnt= len(commentData)
        
        # 댓글 데이터 가공
        k = 0
                    
        for i in commentserializer.data:
            if (int(flag) in i['like']) == True:
                i["isLiked"]=True
            else:
                i["isLiked"]=False
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

            elif slug1 == "2":
                i["CID"] = i["QCID"]
                del i["QCID"]
                del i["QPID"]

            if i["parentID"] == 0:
                i["childComment"] = list()
                i['updateAt'] = datetime.datetime.strptime(i["updateAt"], '%Y-%m-%dT%H:%M:%S.%f').strftime("%Y-%m-%d %H:%M")
                RcommentData.append(i)
            k = k + 1
        
        for i in commentserializer.data:
            if i["parentID"] != 0:
                for j in RcommentData:
                    if i["parentID"] == j["CID"]:
                        #del i["parentID"]
                        del i["UID"]
                        i['updateAt'] = datetime.datetime.strptime(i["updateAt"], '%Y-%m-%dT%H:%M:%S.%f').strftime("%Y-%m-%d %H:%M")
                        j["childComment"].append(i)
                        break

        
        for i in RcommentData:
            del i["parentID"]
            del i["UID"]
        
        # ios 1차원 데이터 작업
        if request.GET.get('mode') is not None and request.GET.get('mode') == "1":
            RcommentData2 = list()
            
            for i in RcommentData:               
            
                temp = i.copy()
                del temp["childComment"]
                temp["reply"]=0
                RcommentData2.append(temp)
                
                if 'childComment' in i:
                    for j in i["childComment"]:
                        j["reply"]=1
                        RcommentData2.append(j)

            RcommentData = RcommentData2

        return JsonResponse({
                'success':True,
                'result' :{'commentdata':RcommentData, 'commentCnt':commentCnt},
                'errorMessage':""
                },            status=status.HTTP_200_OK) 





@swagger_auto_schema(
    method='get',
    operation_description= "검색 API",
    manual_parameters=[
        openapi.Parameter('keyword',openapi.IN_QUERY,type=openapi.TYPE_STRING, description='검색어'),
        openapi.Parameter('quantity',openapi.IN_QUERY,type=openapi.TYPE_INTEGER, description='원하는 수량'),
        openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='원하는 페이지'),
    ],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'bookList' : openapi.Schema('사용자가 선택한 태그', type=openapi.TYPE_ARRAY, items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                            'TITLE':openapi.Schema('책 제목', type=openapi.TYPE_STRING),
                            }
                        )),
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)


@api_view(['GET'])
def PostSearch(request): #책 검색 API
    exceptDict = None    

    if request.method == 'GET' :

        if request.GET.get('keyword') is not None and len(request.GET.get('keyword'))>1:

            quantity = 25 #기본 quntity 값은 25개
            startpagination = 0 #기본 startpagination 값은 0
            endpagination = quantity #기본 endpagination 값은 qunatity값과 동일, page 값이 들어오면 pagination 지원

            keyword = request.GET.get('keyword')
            print(keyword)
            keyword = parse.unquote(keyword)
            print(keyword)

            search = keyword
            
            AnyData = AnyCommunity.objects.filter( Q(title__contains = search) | Q(contents__contains = search) )
            MarData = MarketCommunity.objects.filter( Q(title__contains = search) | Q(contents__contains = search) )
            QnAData = QnACommunity.objects.filter(parentQPID = 0).filter( Q(title__contains = search) | Q(contents__contains = search) )
            
            
            AnySer = AnyCommunitySerializer(AnyData, many = True)
            MarSer = MarketCommunitySerializer(MarData, many = True)
            QnASer = QnACommunitySerializer(QnAData, many = True)
            
            SearchData = list()

            for i in AnySer.data:
                i['PID']  = i['APID']
                i['communityType'] = 0
                i['likeCnt'] = len(i['like'])
                i['replyCnt'] = -1
                i['commentCnt'] =  len(AnyComment.objects.filter(APID = i['APID']))
                del i['like']
                del i['APID']
                SearchData.append(i)
                
            for i in MarSer.data:
                i['PID']  = i['MPID']
                i['communityType'] = 1
                i['likeCnt'] = len(i['like'])
                i['replyCnt'] = -1
                i['commentCnt'] =  len(MarketComment.objects.filter(MPID = i['MPID']))
                del i['like']
                del i['MPID']
                SearchData.append(i)
            
            for i in QnASer.data:
                i['PID']  = i['QPID']
                i['communityType'] = 2
                i['likeCnt'] = len(i['like'])
                i['replyCnt'] = len(QnACommunity.objects.filter(parentQPID = i['QPID']))
                i['commentCnt'] =  len(QnAComment.objects.filter(QPID = i['QPID']))
                del i['like']
                del i['QPID']
                SearchData.append(i)
            

            # 정렬 미구현

            return JsonResponse({'success':True,'result' : SearchData, 'total_size':len(SearchData), 'errorMessage':""}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success':True,'result' : exceptDict, 'errorMessage':"검색어가 없거나 너무 짧습니다."}, status=status.HTTP_400_BAD_REQUEST)    # else :
    else:
        return JsonResponse({'success':False,'result' : exceptDict, 'errorMessage':str(request.method) + " 호출은 지원하지 않습니다." }, status=status.HTTP_403_FORBIDDEN)
        





@swagger_auto_schema(
    method='put',  
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
       request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'comment': openapi.Schema('댓글 내용', type=openapi.TYPE_STRING),        
                    'CID': openapi.Schema('댓글 CID', type=openapi.TYPE_INTEGER),
                    'PID': openapi.Schema('게시글 PID', type=openapi.TYPE_INTEGER),
        },
        required=['comment','CID','PID']
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
def modifyCommunityComment(request,slug):
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
                    commentData = AnyComment.objects.filter(ACID = data['CID'])
                
                elif slug =="1":
                    commentData = MarketComment.objects.filter(MCID = data['CID'])

                elif slug =="2":
                    commentData = QnAComment.objects.filter(QCID = data['CID'])

                if len(userData) != 0 and commentData[0].UID.UID == userID:
                    data['UID']=userData[0].UID
                    data['updateAt']=str(datetime.datetime.utcnow())

                    if slug == "0":
                        data['parentID'] = commentData[0].parentID
                        data['APID'] = data['PID']

                        commentSerializer = AnyCommentSerializer(commentData[0],data = data)

                    elif slug == "1":
                        data['parentID'] = commentData[0].parentID
                        data['MPID'] = data['PID']
                        commentSerializer = MarketCommentSerializer(commentData[0],data = data)

                    elif slug == "2":
                        data['parentID'] = commentData[0].parentID
                        data['QPID'] = data['PID']
                        commentSerializer = QnACommentSerializer(commentData[0],data = data)

                    if commentSerializer.is_valid():
                        commentSerializer.save()
                        return JsonResponse({
                        'success':True,
                        'result' :"댓글 수정 완료",
                        'errorMessage':""
                        })
                    else:
                        return JsonResponse({
                        'success':False,
                        'result' :{},
                        'errorMessage':commentSerializer.errors
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
    operation_description= "slug1 => 0 = '자유게시판', 1 = '장터게시판', 2 = 'QnA게시판', 3 = 'HOT게시판' , slug2 => CID",
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
def commentLike(request,slug1,slug2):
    flag = checkAuth_decodeToken(request)
    
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
        print("slug1",slug1)
        print("slug2",slug2)
        if slug1 == "0": #자게
            queryData = AnyComment.objects.get(ACID = slug2)
        elif slug1 == "1": #장터
            queryData = MarketComment.objects.get(MCID = slug2)
        elif slug1 == "2": # QnA
            queryData = QnAComment.objects.get(QCID = slug2)
        
        if queryData is not None:
            if likeFunction(queryData, flag):
                return JsonResponse({'success':True, 'result':{'isLiked':True}, 'errorMessage':""}, status = status.HTTP_200_OK)
            else:
                return JsonResponse({'success':True, 'result':{'isLiked':False}, 'errorMessage':""}, status = status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"해당 CID의 댓글이 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"해당 호출은 지원하지 않습니다."}, status = status.HTTP_405_Method_Not_Allowed)
