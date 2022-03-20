from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from .models import Book
from .bookserializers import BookPostSerializer
from .auth import authValidation
from django.db.models import Q

import requests
import datetime
import urllib.request
import json
import time

@api_view(['GET'])
def book(request, slug): #책 정보 API
    if authValidation(request) == True:
        try:
            bookData = Book.objects
        except Book.DoesNotExist:
            return JsonResponse({'success':False, 'result': {}, 'errorMessage':"Book에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"}, status=status.HTTP_404_NOT_FOUND)
        if (request.method == 'GET'):
            if slug ==  "0" :
                quantity = 25 #기본 quntity 값은 25개
                startpagination = 0 #기본 startpagination 값은 0
                endpagination = quantity #기본 endpagination 값은 qunatity값과 동일, page 값이 들어오면 pagination 지원
                books = bookData.all()
                if request.GET.get('quantity') is not None: #URL에 'quantity' Query가 들어있으면 값 입력
                    quantity = int(request.GET.get('quantity')) 
                if request.GET.get('page') is not None: #URL에 'page' Query가 들어있으면 값 입력
                    startpagination = (int(request.GET.get('page')) - 1) * quantity
                    endpagination = int(request.GET.get('page')) * quantity
                if request.GET.get('TAG') is not None: #URL에 'page' Query가 들어있으면 값 입력
                    books = bookData.filter(PUBLISHER = request.GET.get('TAG'))
                books = books[startpagination : endpagination]    
                serializer = BookPostSerializer(books, many=True)
                return JsonResponse({'success':True,'result' : serializer.data, 'errorMessage':""}, status=status.HTTP_200_OK)
            else :
                filtered_data = bookData.filter(BID = slug)
                if len(filtered_data) == 0:
                    return JsonResponse({'success':False, 'result':{}, 'errorMessage':"입력한 BID와 일치하는 정보가 없습니다."}, status=status.HTTP_204_NO_CONTENT)
                else:
                    serializer = BookPostSerializer(filtered_data, many = True)
                    return JsonResponse({'success':True, 'result' : serializer.data[0], 'errorMessage':""}, status = status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False,'result' : {}, 'errorMessage':str(request.method) + " 호출은 지원하지 않습니다." }, status=status.HTTP_403_FORBIDDEN)
                    
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
                return JsonResponse({'success':False,'result' : {}, 'errorMessage':"검색어가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success':False,'result' : {}, 'errorMessage':str(request.method) + " 호출은 지원하지 않습니다." }, status=status.HTTP_403_FORBIDDEN)