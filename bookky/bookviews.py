from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from .models import Book
from .bookserializers import BookPostSerializer
from .auth import valid_token

import requests
import datetime
import urllib.request
import json
import time

@api_view(['GET', 'PUT', 'DELETE'])
def book(request, slug):
    print(request.headers.get('Authorization'))
    if request.headers.get('Authorization')is None:
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':"Authroization키가 없음"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        tempToken = request.headers.get('Authorization',None)
        if valid_token(tempToken) == False:
            return JsonResponse({'success':False, 'result': {}, 'errorMessage':"유저 정보가 없음"}, status=status.HTTP_401_UNAUTHORIZED)
        else :
            try:
                bookData = Book.objects
            except Book.DoesNotExist:
                return JsonResponse({'success':False, 'result': {}, 'errorMessage':"Book에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"}, status=status.HTTP_404_NOT_FOUND)
            if (request.method == 'GET'):
                quantity = 25
                if slug ==  "0" :
                    if request.GET.get('quantity') is not None:
                        quantity = int(request.GET.get('quantity'))
                    if request.GET.get('page') is not None:
                        startpagination = (int(request.GET.get('page')) - 1) * quantity
                        endpagination = int(request.GET.get('page')) * quantity
                    books = bookData.all()
                    books = books[startpagination : endpagination]    
                    serializer = BookPostSerializer(books, many=True)
                    return JsonResponse({'success':True,'result' : serializer.data, 'errorMessage':""}, status=status.HTTP_200_OK)
                else :
                    filtered_data = bookData.filter(BID = slug)
                    if len(filtered_data) == 0:
                        return JsonResponse({'success':False, 'result':{}, 'errorMessage':"입력한 BID와 일치하는 정보가 없습니다."}, status=status.HTTP_204_NO_CONTENT)
                    else:
                        serializer = BookPostSerializer(filtered_data, many = True)
                        return JsonResponse({'success':True, 'result' : serializer.data[0]}, status = status.HTTP_200_OK)            
            elif request.mtehod == 'PUT':
                return
            elif request.mtehod == 'DELETE':
                return