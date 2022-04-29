from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg import openapi

from bookky.auth.auth import checkAuth_decodeToken
from bookky_backend import settings
from bookky.models import Book, FavoriteBook, Tag
from bookky.serializers.bookserializers import BookPostSerializer, BookGetSerializer
from bookky.auth.auth import authValidation
from django.db.models import Q

import requests
import datetime
import urllib.request
import json
import time

@swagger_auto_schema(
    method='get',
    operation_description= "slug = 0은 TAG구분없이 보냄, slug = 1은 dummyAPI로 태그로 구분해서 보냄",
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
        bookData = Book.objects
    except Book.DoesNotExist:
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
            filtered_data = bookData.filter(BID = slug)
            is_favorite = False
            if len(filtered_data) == 0:
                return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"입력한 BID와 일치하는 정보가 없습니다."}, status=status.HTTP_204_NO_CONTENT)
            else:
                if request.headers.get('access_token',None) is not None:
                    userID = checkAuth_decodeToken(request)
                    print(userID)
                    if userID == 1:
                        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT토큰입니다."}, status = status.HTTP_401_UNAUTHORIZED)
                    elif userID == 2:
                        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"만료된 토큰입니다."}, status = status.HTTP_403_FORBIDDEN)
                    else:        
                        queryData = FavoriteBook.objects.filter(UID = userID)
                        queryData = queryData.filter(BID = slug)
                        if len(queryData) != 0:
                            is_favorite = True
                serializer = BookPostSerializer(filtered_data, many = True)
                temp = serializer.data[0]
                temp['tagName'] = findBooksTagName(slug)
                return JsonResponse({'success':True, 'result' : {'bookList':serializer.data[0],'isFavorite':is_favorite}, 'errorMessage':""}, status = status.HTTP_200_OK)
    else:
        return JsonResponse({'success':False,'result' : exceptDict, 'errorMessage':str(request.method) + " 호출은 지원하지 않습니다."}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def bookSearch(request): #책 검색 API
    if authValidation(request) == True :
        if request.method == 'GET' :
            if request.GET.get('searchKey') is not None:
                search = request.GET.get('searchKey')
                searchData = Book.objects.filter(
                    Q(TITLE__icontains = search) | #제목
                    Q(AUTHOR__icontains = search) | #저자
                    Q(BOOK_INTRODUCTION__icontains = search) | #책 소개
                    Q(PUBLISHER__icontains = search) | #책 출판사
                    Q(TAG__icontains = search) #태그
                )
                serializer = BookPostSerializer(searchData, many = True)
                return JsonResponse({'success':True,'result' : serializer.data, 'errorMessage':""}, status=status.HTTP_200_OK)
            else :
                return JsonResponse({'success':False,'result' : exceptDict, 'errorMessage':"검색어가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success':False,'result' : exceptDict, 'errorMessage':str(request.method) + " 호출은 지원하지 않습니다." }, status=status.HTTP_403_FORBIDDEN)
        
def bookUpdate(request):
    json_bookData = dict()

    with open("BookData1.json","r") as rt_json:
        json_bookData = json.load(rt_json)
    for i in json_bookData :
        data = i.get('Allah_BID')
        tempData = Book.objects.filter(Allah_BID = data)
        print(tempData[0].thumbnailImage)
        if(len(tempData) != 0):
            print(str(settings.MEDIA_ROOT)+str(data)+".png")
        
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
                'thumbnailImage': "http://203.255.3.144:8010/thumbnail/"+str(data)+".png"
            }
            print(tempDic['thumbnailImage'])
            serializer = BookPostSerializer(tempData[0], data=tempDic)
            if serializer.is_valid():
                serializer.save()
            else :
                print(serializer.errors)
        else:
            continue
    return JsonResponse({'success':True})


def findBooksTagName(BID):
    bookQuery = Book.objects.get(BID = BID)
    tagQuery = Tag.objects
    tempList = bookQuery.TAG
    tagNames = []
    for i in tempList:
        temp = tagQuery.get(TID = i)
        tagNames.append(temp.nameTag)
    return tagNames
    
@swagger_auto_schema(
    method='get',
    operation_description= "slug에 태그번호를 입력하면 해당 태그의 데이터를 quantity와 page로 나누어서 뿌려줌",
    manual_parameters=[
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
                        'bookList' : openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'tag': openapi.Schema('태그이름', type=openapi.TYPE_STRING),
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
                        )
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
        bookQuery = Book.objects
        tagQuery = Tag.objects
        if len(tagQuery.filter(TID = tagNumber)) == 0:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessag':"해당하는 태그가 존재하지 않습니다."}, status = status.HTTP_400_BAD_REQUEST)
        bookData = bookQuery.filter(TAG__contains = [tagNumber])
        if len(bookData) == 0:
            return JsonResponse({'success':True, 'result':exceptDict, 'errorMessage':"Query 결과 값이 없습니다."}, status = status.HTTP_204_NO_CONTENT)        
        if request.GET.get('quantity') is not None: #URL에 'quantity' Query가 들어있으면 값 입력
            quantity = int(request.GET.get('quantity')) 
        if request.GET.get('page') is not None: #URL에 'page' Query가 들어있으면 값 입력
            startpagination = (int(request.GET.get('page')) - 1) * quantity
            endpagination = int(request.GET.get('page')) * quantity
            if startpagination > len(bookData):
                startpagination = startpagination - len(books)
            if endpagination > len(bookData):
                endpagination = len(bookData) - 1
        bookData = bookData[startpagination : endpagination]               
        bookSerializer = BookGetSerializer(bookData, many=True)
        temp = tagQuery.get(TID=tagNumber)
        resultDict = {'tag':temp.nameTag,'data':bookSerializer.data}
        return JsonResponse({'success':True, 'result':{'bookList':resultDict}, 'errorMessage':""},status=status.HTTP_200_OK)