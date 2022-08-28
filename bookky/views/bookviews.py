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

import requests
import datetime
import urllib.request
import json
import time

@swagger_auto_schema(
    method='get',
    operation_description= "slug = 0은 모든 책을 보냄, 그외에는 slug에 책 BID를 넣어 책의 상세정보 받아옴",
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
                        'bookList' : openapi.Schema('사용자가 선택한 태그', type=openapi.TYPE_ARRAY, items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                            'TITLE':openapi.Schema('책 제목', type=openapi.TYPE_STRING),
                            'SUBTITLE':openapi.Schema('책 부제', type=openapi.TYPE_STRING),
                            'AUTHOR':openapi.Schema('책 저자', type=openapi.TYPE_STRING),
                            'ISBN':openapi.Schema('책 ISBN코드', type=openapi.TYPE_STRING),
                            'PUBLISHER':openapi.Schema('책 출판사', type=openapi.TYPE_STRING),
                            'PRICE':openapi.Schema('책 가격', type=openapi.TYPE_STRING),
                            'PAGE':openapi.Schema('책 페이지 수', type=openapi.TYPE_STRING),
                            'BOOK_INDEX':openapi.Schema('책 목차', type=openapi.TYPE_STRING),
                            'BOOK_INTRODUCTION':openapi.Schema('책 소개', type=openapi.TYPE_STRING),
                            'Allah_BID' : openapi.Schema('책 알라딘 코드', type=openapi.TYPE_STRING),
                            'PUBLISH_DATE' : openapi.Schema('책 출판일', type=openapi.TYPE_STRING),
                            'thumbnail' : openapi.Schema('책 이미지', type=openapi.TYPE_STRING),
                            'thumbnailImage': openapi.Schema('책 이미지', type=openapi.TYPE_STRING),
                            'tagData' :openapi.Schema(
                                type = openapi.TYPE_OBJECT,
                                properties={
                                    'tag':openapi.Schema('태그이름', type=openapi.TYPE_STRING),
                                    'TMID':openapi.Schema('태그아이디',type=openapi.TYPE_INTEGER)
                                }
                            ) 
                            }
                        )),
                        'isFavorite' : openapi.Schema('사용자가 선택한 태그', type=openapi.TYPE_BOOLEAN),
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
@api_view(['GET'])
def book(request, slug): #책 정보 API
    exceptDict = None
    try:
        bookData = TempBook.objects
    except TempBook.DoesNotExist:
        return JsonResponse({'success':False, 'result': exceptDict, 'errorMessage':"Book에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"}, status=status.HTTP_404_NOT_FOUND)
    if (request.method == 'GET'):
        if slug == "0": #dummy 책api
            quantity = 25 #기본 quntity 값은 25개
            startpagination = 0 #기본 startpagination 값은 0
            endpagination = quantity #기본 endpagination 값은 qunatity값과 동일, page 값이 들어오면 pagination 지원
            books = bookData.all()
            if request.GET.get('quantity') is not None: #URL에 'quantity' Query가 들어있으면 값 입력
                quantity = int(request.GET.get('quantity')) 
            if request.GET.get('page') is not None: #URL에 'page' Query가 들어있으면 값 입력
                startpagination = (int(request.GET.get('page')) - 1) * quantity
                endpagination = int(request.GET.get('page')) * quantity
                if startpagination > len(books):
                    startpagination = startpagination - len(books)
                if endpagination > len(books):
                    endpagination = len(books) - 1
            books = books[startpagination : endpagination]   
            serializer = BookPostSerializer(books, many=True)
            return JsonResponse({
                'success':True,
                'result' :{'bookList':serializer.data},
                'errorMessage':""
                }, 
                status=status.HTTP_200_OK)
        else :
            #slug 정규식처리 필요함
            filtered_data = bookData.filter(TBID = slug)
            is_favorite = False
            userID = None
            tempReviewQuery = None
            if len(filtered_data) == 0:
                return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"입력한 BID와 일치하는 정보가 없습니다."}, status=status.HTTP_204_NO_CONTENT)
            else:
                if request.headers.get('access_token',None) is not None:
                    if len(request.headers.get('access_token',None)) != 0:
                        userID = checkAuth_decodeToken(request)
                        if userID == -1:
                            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
                        elif userID == -2:
                            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_401_UNAUTHORIZED)
                        else:        
                            queryData = FavoriteBook.objects.filter(UID = userID)
                            queryData = queryData.filter(TBID = slug)
                            if len(queryData) != 0:
                                is_favorite = True
                serializer = BookPostSerializer(filtered_data, many = True)
                temp = serializer.data[0]
                temp['tagData'] = findBooksTagName(slug)
                if userID is not None:
                    reviewQuery = Review.objects.filter(TBID=slug)
                    reviewSerializer = ReviewGetSerializer(reviewQuery, many = True)
                    tempReviewQuery = reviewSerializer.data
                    for i in tempReviewQuery:
                        if i['UID'] == userID:
                            i['isAccessible'] = True
                        else :
                            i['isAccessible'] = False
                        tempUserQuery = User.objects.get(UID=i['UID'])
                        i['createAt'] = datetime.datetime.strptime(i["createAt"], '%Y-%m-%dT%H:%M:%S.%f').strftime("%Y-%m-%d %H:%M")
                        i['likeCnt'] = len(i['like'])
                        if i['like'].count(userID) > 0:
                            i['isLiked'] = True
                        else:
                            i['isLiked'] = False
                        del i['like']
                        i['nickname'] = tempUserQuery.nickname
                        tempQuery = TempBook.objects.get(TBID = i['TBID'])
                        i['AUTHOR'] = tempQuery.AUTHOR
                        i['bookTitle'] = tempQuery.TITLE
                        i['thumbnail'] = tempQuery.thumbnailImage

                return JsonResponse({'success':True, 'result' : {'bookList':serializer.data[0],'isFavorite':is_favorite, 'reviewList':tempReviewQuery}, 'errorMessage':""}, status = status.HTTP_200_OK)
    else:
        return JsonResponse({'success':False,'result' : exceptDict, 'errorMessage':str(request.method) + " 호출은 지원하지 않습니다."}, status=status.HTTP_403_FORBIDDEN)

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
                        'searchData' : openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'bookList' : openapi.Schema('사용자가 선택한 태그', type=openapi.TYPE_ARRAY, items=openapi.Items(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'TITLE':openapi.Schema('책 제목', type=openapi.TYPE_STRING),
                                        'AUTHOR':openapi.Schema('책 저자', type=openapi.TYPE_STRING),
                                        'BOOK_INTRODUCTION':openapi.Schema('책 소개', type=openapi.TYPE_STRING),
                                        'PUBLISH_DATE' : openapi.Schema('책 출판일', type=openapi.TYPE_STRING),
                                        'thumbnailImage': openapi.Schema('책 이미지', type=openapi.TYPE_STRING),
                                        'tagData' :openapi.Schema(
                                            type = openapi.TYPE_OBJECT,
                                            properties={
                                                'tag':openapi.Schema('태그이름', type=openapi.TYPE_STRING),
                                                'TMID':openapi.Schema('태그아이디',type=openapi.TYPE_INTEGER)
                                            })
                                    }
                                )),
                                'total' : openapi.Schema('총 페이지 수 ',type=openapi.TYPE_INTEGER)
                            }
                        )     
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
@api_view(['GET'])
def bookSearch(request): #책 검색 API
    exceptDict = None    
    if request.method == 'GET' :
        #slug 정규식 처리 필요함, 한국어 처리 필요
        if request.GET.get('keyword') is not None and len(request.GET.get('keyword'))>1:
            quantity = 25 #기본 quntity 값은 25개
            startpagination = 0 #기본 startpagination 값은 0
            endpagination = quantity #기본 endpagination 값은 qunatity값과 동일, page 값이 들어오면 pagination 지원
            keyword = request.GET.get('keyword')
            keyword = parse.unquote(keyword)
            keyword = keyword.replace(" ", "")
            search = keyword
            searchData = TempBook.objects.filter(
                Q(searchName__icontains = search) | #제목
                # Q(AUTHOR__icontains = search) | #저자
                # Q(BOOK_INTRODUCTION__icontains = search) | #책 소개
                # Q(PUBLISHER__icontains = search) | #책 출판사
                Q(TAG__icontains = search) #태그
            )
            tagSearchData = TagModel.objects.filter(
                Q(searchName__icontains = search)
            )
            serializer = BookSearchSerializer(searchData, many = True)
            tagData = list()
            for i in tagSearchData:
                tagData += TempBook.objects.filter(TAG__contains = [i.TMID])
            tagSerializer = BookSearchSerializer(tagData, many=True)
            dataList = serializer.data
            dataList = dataList + tagSerializer.data
            tagSet = set()
            bookSet = set()
            anotherList = set() #교집합으로 우선 출력 해야할 책을 뽑아야함 나중에 생각하자
            for i in serializer.data:
                bookSet.add(i['TBID'])
            for i in tagSerializer.data:
                tagSet.add(i['TBID'])
            for i in dataList:
                anotherList.add(i['TBID'])
            intersectionSet = tagSet & bookSet
            diffSet = anotherList - intersectionSet
            completeSet = list(intersectionSet) + list(diffSet)

            bookData = list()
            for i in completeSet:
                bookData.append(TempBook.objects.get(TBID = i))
            totalPage = len(bookData)//quantity
            if len(bookData) % quantity != 0:
                totalPage = int(totalPage) + 1
            if request.GET.get('quantity') is not None: #URL에 'quantity' Query가 들어있으면 값 입력
                if int(request.GET.get('quantity')) > len(bookData):
                    if int(request.GET.get('page')) > totalPage:
                        return JsonResponse({'success':True,'result' : exceptDict, 'errorMessage':"검색어가 없습니다."}, status=status.HTTP_204_NO_CONTENT)    # else :    
                    dataList = BookSearchSerializer(bookData, many=True)
                    return JsonResponse({'success':True,'result' : {'searchData' : dataList.data, 'total':1}, 'errorMessage':""}, status=status.HTTP_200_OK)
                quantity = int(request.GET.get('quantity'))
                totalPage = len(bookData)//quantity
                if len(bookData) % quantity != 0:
                    totalPage = int(totalPage) + 1
            if request.GET.get('page') is not None: #URL에 'page' Query가 들어있으면 값 입력
                if int(request.GET.get('page')) > totalPage:
                    return JsonResponse({'success':True,'result' : exceptDict, 'errorMessage':"검색어가 없습니다."}, status=status.HTTP_204_NO_CONTENT)    # else :    
                startpagination = (int(request.GET.get('page')) - 1) * quantity
                endpagination = int(request.GET.get('page')) * quantity
                if startpagination > len(bookData):
                    startpagination = startpagination - len(bookData)
                if endpagination > len(bookData):
                    endpagination = len(bookData) - 1
            bookData = bookData[startpagination : endpagination]   
            dataList = BookSearchSerializer(bookData, many=True)
            for i in dataList.data:
                i['tagData'] = findBooksTagName(int(i['TBID']))
            if len(dataList.data) == 0:
                return JsonResponse({'success':True,'result' : exceptDict, 'errorMessage':"검색어가 없습니다."}, status=status.HTTP_204_NO_CONTENT)    # else :    
            return JsonResponse({'success':True,'result' : {'searchData' : dataList.data, 'total':totalPage}, 'errorMessage':""}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success':True,'result' : exceptDict, 'errorMessage':"검색어가 없습니다."}, status=status.HTTP_204_NO_CONTENT)    # else :
    else:
        return JsonResponse({'success':False,'result' : exceptDict, 'errorMessage':str(request.method) + " 호출은 지원하지 않습니다." }, status=status.HTTP_403_FORBIDDEN)
        
def bookUpdate(request):
    json_bookData = dict()

    with open("BookData4.json","r") as rt_json:
        json_bookData = json.load(rt_json)
    for i in json_bookData :
        data = i.get('Allah_BID')
        tempData = TempBook.objects.filter(Allah_BID = data)
        if(len(tempData) != 0):
            tempDic ={
                'TITLE':tempData[0].TITLE, 
                'SUBTITLE':tempData[0].SUBTITLE,
                'AUTHOR':tempData[0].AUTHOR,
                'ISBN':tempData[0].ISBN,
                'PUBLISHER':tempData[0].PUBLISHER,
                'PRICE':tempData[0].PRICE,
                'PAGE':tempData[0].PAGE,
                'BOOK_INDEX':tempData[0].BOOK_INDEX,
                'BOOK_INTRODUCTION':tempData[0].BOOK_INTRODUCTION,
                'Allah_BID' : tempData[0].Allah_BID,
                'PUBLISH_DATE' : tempData[0].PUBLISH_DATE,
                'thumbnail' : tempData[0].thumbnail,
                'thumbnailImage': "http://203.255.3.144:8010/thumbnail/bookThumbnail/"+str(data)+".png"
            }
            serializer = BookPostSerializer(tempData[0], data=tempDic)
            if serializer.is_valid():
                serializer.save()
            else :
                print(serializer.errors)
        else:
            continue
    return JsonResponse({'success':True})


def findBooksTagName(TBID):
    bookQuery = TempBook.objects.get(TBID = TBID)
    tagQuery = TagModel.objects
    tempList = bookQuery.TAG
    if tempList is not None:
        tagNames = []
        for i in tempList:
            if i == 0:
                continue
            temp = tagQuery.get(TMID = i)
            tagNames.append({'tag':temp.nameTag, 'TMID':temp.TMID})
    return tagNames
    
@swagger_auto_schema(
    method='get',
    operation_description= "slug에 태그번호를 입력하면 해당 태그의 데이터를 quantity와 page로 나누어서 뿌려줌",
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
                        'bookList' : openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'tag': openapi.Schema('태그이름', type=openapi.TYPE_STRING),
                                    'TMID':openapi.Schema('태그아이디', type=openapi.TYPE_INTEGER),
                                    'data' :openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Items(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'BID':openapi.Schema('BID', type=openapi.TYPE_INTEGER),
                                                'TITLE':openapi.Schema('책 제목', type=openapi.TYPE_STRING),
                                                'AUTHOR':openapi.Schema('책 저자', type=openapi.TYPE_STRING),
                                                'thumbnailImage':openapi.Schema('책 이미지', type=openapi.TYPE_STRING),
                                            }
                                        )
                                    )   
                                }
                            )
                        ),
                        'total' : openapi.Schema('총 페이지 수 ',type=openapi.TYPE_INTEGER)
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
@api_view(['GET'])
def getBooksByTag(request, slug):
    exceptDict = None
    if request.method == 'GET':
        quantity = 25 #기본 quntity 값은 25개
        startpagination = 0 #기본 startpagination 값은 0
        endpagination = quantity #기본 endpagination 값은 qunatity값과 동일, page 값이 들어오면 pagination 지원
        tagNumber = int(slug)
        bookQuery = TempBook.objects
        tagQuery = TagModel.objects

        if request.headers.get('access_token', None) is not None and len(request.headers.get('access_token', None)) != 0: #회원일 때
            flag = checkAuth_decodeToken(request)
            if flag == -1:
                return JsonResponse({'success':False, 'result':{'bookList':exceptDict,'communityList':[],'userData':None}, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
            elif flag == -2:
                return JsonResponse({'success':False, 'result':{'bookList':exceptDict,'communityList':[],'userData':None}, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)
            if slug == "9999":
                bookData = todayRecommendBooks(flag)
        if slug != "9999":
            if len(tagQuery.filter(TMID = tagNumber)) == 0:
                return JsonResponse({'success':False, 'result':exceptDict, 'errorMessag':"해당하는 태그가 존재하지 않습니다."}, status = status.HTTP_400_BAD_REQUEST)
            bookData = bookQuery.filter(TAG__contains = [tagNumber])
            if len(bookData) == 0:
                return JsonResponse({'success':True, 'result':exceptDict, 'errorMessage':"Query 결과 값이 없습니다."}, status = status.HTTP_204_NO_CONTENT)    
        totalPage = len(bookData)//quantity
        if len(bookData) % quantity != 0:
            totalPage = int(totalPage) + 1
        if request.GET.get('quantity') is not None: #URL에 'quantity' Query가 들어있으면 값 입력
            quantity = int(request.GET.get('quantity')) 
            totalPage = len(bookData)//quantity
            if len(bookData) % quantity != 0:
                totalPage = int(totalPage) + 1
        if request.GET.get('page') is not None: #URL에 'page' Query가 들어있으면 값 입력
            startpagination = (int(request.GET.get('page')) - 1) * quantity
            endpagination = int(request.GET.get('page')) * quantity
            if startpagination > len(bookData):
                startpagination = startpagination - len(books)
            if endpagination > len(bookData):
                if len(bookData) < 25:
                    endpagination = len(bookData)
                else:
                    endpagination = len(bookData) - 1
        bookData = bookData[startpagination : endpagination]
        if slug != "9999":
            bookSerializer = BookGetSerializer(bookData, many=True)
            bookList = bookSerializer.data
            temp = tagQuery.get(TMID=tagNumber)
            tagName = temp.nameTag
            TMID = temp.TMID
        else:
            bookList = bookData
            tagName = "오늘의 추천 도서"
            TMID = "9999"
        resultDict = {'tag':tagName,'TMID':TMID,'data':bookList, 'total' : totalPage}
        return JsonResponse({'success':True, 'result':{'bookList':resultDict}, 'errorMessage':""},status=status.HTTP_200_OK)


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
                        'searchData' : openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'bookList' : openapi.Schema('사용자가 선택한 태그', type=openapi.TYPE_ARRAY, items=openapi.Items(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'TITLE':openapi.Schema('책 제목', type=openapi.TYPE_STRING),
                                        'AUTHOR':openapi.Schema('책 저자', type=openapi.TYPE_STRING),
                                        'BOOK_INTRODUCTION':openapi.Schema('책 소개', type=openapi.TYPE_STRING),
                                        'PUBLISH_DATE' : openapi.Schema('책 출판일', type=openapi.TYPE_STRING),
                                        'thumbnailImage': openapi.Schema('책 이미지', type=openapi.TYPE_STRING),
                                        'tagData' :openapi.Schema(
                                            type = openapi.TYPE_OBJECT,
                                            properties={
                                                'tag':openapi.Schema('태그이름', type=openapi.TYPE_STRING),
                                                'TMID':openapi.Schema('태그아이디',type=openapi.TYPE_INTEGER)
                                            })
                                    }
                                )),
                                'total' : openapi.Schema('총 페이지 수 ',type=openapi.TYPE_INTEGER)
                            }
                        )     
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
@api_view(['GET'])
def communityAddBooks(request): #책 검색 API
    exceptDict = None    
    if request.method == 'GET' :
        #slug 정규식 처리 필요함, 한국어 처리 필요
        if request.GET.get('keyword') is not None and len(request.GET.get('keyword'))>1:
            quantity = 25 #기본 quntity 값은 25개
            startpagination = 0 #기본 startpagination 값은 0
            endpagination = quantity #기본 endpagination 값은 qunatity값과 동일, page 값이 들어오면 pagination 지원
            keyword = request.GET.get('keyword')
            keyword = parse.unquote(keyword)
            search = keyword
            searchData = TempBook.objects.filter(
                Q(searchName__icontains = search) | #제목
                # Q(AUTHOR__icontains = search) | #저자
                # Q(BOOK_INTRODUCTION__icontains = search) | #책 소개
                # Q(PUBLISHER__icontains = search) | #책 출판사
                Q(TAG__icontains = search) #태그
            )
            tagSearchData = TagModel.objects.filter(
                Q(searchName__icontains = search)
            )
            serializer = BookSimpleSerializer(searchData, many = True)
            tagData = list()
            for i in tagSearchData:
                tagData += TempBook.objects.filter(TAG__contains = [i.TMID])
            tagSerializer = BookSimpleSerializer(tagData, many=True)
            dataList = serializer.data
            dataList = dataList + tagSerializer.data
            tagSet = set()
            bookSet = set()
            anotherList = set() #교집합으로 우선 출력 해야할 책을 뽑아야함 나중에 생각하자
            for i in serializer.data:
                bookSet.add(i['TBID'])
            for i in tagSerializer.data:
                tagSet.add(i['TBID'])
            for i in dataList:
                anotherList.add(i['TBID'])
            intersectionSet = tagSet & bookSet
            diffSet = anotherList - intersectionSet
            completeSet = list(intersectionSet) + list(diffSet)

            bookData = list()
            totalPage = len(bookData)/quantity
            if len(bookData) % quantity != 0:
                totalPage = (totalPage) + 1
            for i in completeSet:
                bookData.append(TempBook.objects.get(TBID = i))
            if request.GET.get('quantity') is not None: #URL에 'quantity' Query가 들어있으면 값 입력
                quantity = int(request.GET.get('quantity'))
                totalPage = len(bookData)/quantity
                if len(bookData) % quantity != 0:
                    totalPage = int(totalPage) + 1
            if request.GET.get('page') is not None: #URL에 'page' Query가 들어있으면 값 입력
                startpagination = (int(request.GET.get('page')) - 1) * quantity
                endpagination = int(request.GET.get('page')) * quantity
                if startpagination > len(bookData):
                    startpagination = startpagination - len(bookData)
                if endpagination > len(bookData):
                    endpagination = len(bookData) - 1
            bookData = bookData[startpagination : endpagination]   
            dataList = BookSimpleSerializer(bookData, many=True)
            for i in dataList.data:
                i['tagData'] = findBooksTagName(i['TBID'])
            if len(dataList.data) == 0:
                return JsonResponse({'success':True,'result' : exceptDict, 'errorMessage':"검색어가 없습니다."}, status=status.HTTP_204_NO_CONTENT)    # else :    
            return JsonResponse({'success':True,'result' : {'searchData' : dataList.data, 'total':totalPage}, 'errorMessage':""}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success':True,'result' : exceptDict, 'errorMessage':"검색어가 없습니다."}, status=status.HTTP_204_NO_CONTENT)    # else :
    else:
        return JsonResponse({'success':False,'result' : exceptDict, 'errorMessage':str(request.method) + " 호출은 지원하지 않습니다." }, status=status.HTTP_403_FORBIDDEN)