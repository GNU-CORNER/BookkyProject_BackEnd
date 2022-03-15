from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from .models import Book, User
from .bookserializers import BookPostSerializer
from .userserializers import UserRegisterSerializer, UserUpdateSerializer

import requests
import datetime
import urllib.request
import json
import time

#크롤링 해서 나온 데이터를 DB에 저장하는 함수
def saveAPIDatafromCrawl():
    #crawlling 해서 나온 데이터를 정의
    crawlData = {}
    jsonData = JSONParser().parse(crawlData)
    parseSerializer = BookPostSerializer(data = jsonData) #BookPostSerializer 양식에 맞춰서 데이터를 넣어야함
    if parseSerializer.is_valid():
        parseSerializer.save()
        return JsonResponse({'success':True, 'result':parseSerializer.data,'errorMessage':""}, status = status.HTTP_201_CREATED)
    else:
        print(request.body)
        print(parseSerializer.errors)
        return JsonResponse({'success':False, 'result':{}, 'errorMessage':"올바르지 않는 Key값이 입력되었음."},status = status.HTTP_400_BAD_REQUEST)


#사용자 로그인, 회원가입, 회원정보 업데이트, 회원탈퇴 API
@api_view(['POST', 'PUT', 'DELETE'])
def userSign(request):                     
    try:
        data = JSONParser().parse(request)
    except User.DoesNotExist: #User 데이터베이스가 존재하지 않을 때, 혹은 DB와의 연결이 끊겼을 때 출력
        return JsonResponse({'success':False, 'result': {}, 'errorMessage':"User에 대한 데이터베이스가 존재하지 않거나, DB와의 연결이 끊어짐"},status=status.HTTP_404_NOT_FOUND)

    #회원가입, 로그인
    if (request.method == 'POST'):
        userData = User.objects.filter(email=data['email'])
        if data['email'] is not None:
            if(len(userData.filter(email=data['email']))) != 0: #로그인 인증 인가를 통해서 생각 해봐야 할듯
                filteredData = userData.filter(email=data['email'])
                serializer = UserRegisterSerializer(filteredData, many=True)
                return JsonResponse({"success" : True, "result": serializer.data[0], 'errorMessage':""}, status=status.HTTP_202_ACCEPTED)
            
            elif(len(userData.filter(email=data['email']))) == 0: #회원가입 request에 넘어온 UID값과 DB안의 UID와 비교하여 존재하지 않으면, 회원가입으로 생각함
                userSerializer = UserRegisterSerializer(data = data)
                if userSerializer.is_valid():
                    userSerializer.save()
                    return JsonResponse({'success': True, 'result':userSerializer.data,'errorMessage':""}, status = status.HTTP_201_CREATED)
            
                else:
                    return JsonResponse({'success' : False, "result": {}}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success' : False, "result": {}}, status=status.HTTP_400_BAD_REQUEST)

    #회원정보 업데이트
    elif (request.method == 'PUT'):
        userData = User.objects.filter(email=data['email'])
        if data['uid'] is not None:
            if len(userData) == 0 :
                return JsonResponse({'success':False,'result': {}}, safe=False, status=status.HTTP_204_NO_CONTENT)
            else:
                filtTmp = UserUpdateSerializer(userData, many=True)
                if "name" not in data:
                    data['name'] = filtTmp.data[0]['name']
                userData = userData.get()
                serializer = UserUpdateSerializer(userData,data = data)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse({'success':True,'result': serializer.data}, safe=False, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({'success':False,'result': {}}, safe=False, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success':False, 'result':{}},status=status.HTTP_400_BAD_REQUEST)

    #회원탈퇴
    elif (request.method == 'DELETE'):
        userData = User.objects.filter(email=data['email'])
        if data['email'] is not None:
            if len(userData) == 0 :
                return JsonResponse({'success':False,'result': {}}, safe=False, status=status.HTTP_204_NO_CONTENT)
            else:
                filteredData = userData.filter(email=data['email'])
                filteredData.delete()
                return JsonResponse({'success':True, 'result':{}},status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False, 'result':{}},status=status.HTTP_400_BAD_REQUEST)


def read_insert(request):
    json_bookData = dict()

    with open("test.json","r") as rt_json:
        json_bookData = json.load(rt_json)
    print(json_bookData)
    
    for i in json_bookData :
        data = {
            'TITLE':i.get('TITLE'), 
            'SUBTITLE':i.get('SUBTITLE'),
            'AUTHOR':i.get('AUTHOR'),
            'ISBN':i.get('ISBN'),
            'PUBLISHER':i.get('PUBLISHER'),
            'PRICE':i.get('PRICE'),
            'PAGE':i.get('PAGE') ,
            'BOOK_INDEX':i.get('BOOK_INDEX'),
            'BOOK_INTRODUCTION':i.get('BOOK_INTRODUCTION'),
            'Allah_BID' : int(i.get('Allah_BID')),
            'PUBLISH_DATE' : i.get('PUBLISH_DATE'),
        }
        serializer = BookPostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)
    return JsonResponse({})
    