from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from bookky.models import TagModel, TempBook
from bookky.serializers.tagserializers import TagSerializer
from bookky.serializers.bookserializers import BookPostSerializer, BookGetSerializer
from django.core.mail import EmailMessage
from bookky.auth.auth import authValidation

import requests
import datetime
import urllib.request
import json
import time

# #크롤링 해서 나온 데이터를 DB에 저장하는 함수
# def saveAPIDatafromCrawl():
#     #crawlling 해서 나온 데이터를 정의
#     crawlData = {}
#     jsonData = JSONParser().parse(crawlData)
#     parseSerializer = BookPostSerializer(data = jsonData) #BookPostSerializer 양식에 맞춰서 데이터를 넣어야함
#     if parseSerializer.is_valid():
#         parseSerializer.save()
#         return JsonResponse({'success':True, 'result':parseSerializer.data,'errorMessage':""}, status = status.HTTP_201_CREATED)
#     else:
#         print(parseSerializer.errors)
#         return JsonResponse({'success':False, 'result':{}, 'errorMessage':"올바르지 않는 Key값이 입력되었음."},status = status.HTTP_400_BAD_REQUEST)

# def read_insert(request):
#     tempTagList = [1,2,5]
#     bookQuery = Book.objects
#     tagQuery = Tag.objects
#     bookList = []
#     for i in tempTagList:
#         temp = tagQuery.get(TID = i)
#         bookTemp = bookQuery.filter(TAG__contains = [i])
#         serializer = BookGetSerializer(bookTemp, many=True)
#         bookList.append({'tag':temp.nameTag, 'data':serializer.data})

#     return JsonResponse({'data':bookList})
#     # json_bookData = dict()

#     # with open("tag.json","r") as rt_json:
    #     json_bookData = json.load(rt_json)
    
    # for i in json_bookData:
    #     temp = {'nameTag':i.get('Tag'), 'contents':i.get('Elements')}
    #     serializer = TagSerializer(data = temp)
    #     if serializer.is_valid() :
    #         serializer.save()
    #     else:
    #         print(serializer.errors)

    # for i in range(len(json_bookData)):
    
    #     Allah_BID = json_bookData[i]["Allah_BID"]
    #     Tag = json_bookData[i]["Tag"]
    #     print(Allah_BID, Tag)
    #     if len(bookData.filter(Allah_BID = str(Allah_BID))) == 0 :
    #         return JsonResponse({'success':False,'result': {}}, safe=False, status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         bookData1 = bookData.get(Allah_BID = str(Allah_BID))
    #         bookData1.TAG = Tag
    #         bookData1.save()
            
    # return JsonResponse({'success':True,'result': 'Gang', 'errorMessage':""}, safe=False, status=status.HTTP_200_OK)    

    #print(type(request.headers.get('Authorization',None)))
    # tokenA = request.headers.get('Authorization',None)
    # email = EmailMessage('안녕하세요 북키에요!', tokenA, to=['ldh990320ldh@gmail.com', 'kws7327@gmail.com', 'dlsgur3845@gmail.com', 'nugulhie@gmail.com', 'dnjs45077@gmail.com'])
    # email.send()
    # return JsonResponse({})

# def read_insert(request):
#     json_bookData = dict()

#     with open("BookData4.json","r") as rt_json:
#         json_bookData = json.load(rt_json)
    
    # for i in json_bookData :
    #     data = {
    #         'TITLE':i.get('TITLE'), 
    #         'SUBTITLE':i.get('SUBTITLE'),
    #         'AUTHOR':i.get('AUTHOR'),
    #         'ISBN':i.get('ISBN'),
    #         'PUBLISHER':i.get('PUBLISHER'),
    #         'PRICE':i.get('PRICE'),
    #         'PAGE':i.get('PAGE') ,
    #         'BOOK_INDEX':i.get('BOOK_INDEX'),
    #         'BOOK_INTRODUCTION':i.get('BOOK_INTRODUCTION'),
    #         'Allah_BID' : int(i.get('Allah_BID')),
    #         'PUBLISH_DATE' : i.get('PUBLISH_DATE'),
    #         'thumbnail' : i.get('thumbnail')
    #     }
    #     serializer = BookPostSerializer(data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #     else:
    #         print(serializer.errors)
#     return JsonResponse({})
    
# @api_view(['POST'])
# def testAuthorization(request):
#     flag = authValidation(request)
#     if flag == True:
#         return JsonResponse({'success':True})
#     elif flag == 0:
#         return JsonResponse({'success':False, 'result': {}, 'errorMessage':"유효하지 않은 토큰입니다."}, status=status.HTTP_401_UNAUTHORIZED) #JWT 토큰이 없을 때
#     elif flag == 2:
#         return JsonResponse({'success':False, 'result': {}, 'errorMessage':"기간이 지난 토큰입니다."}, status=status.HTTP_403_FORBIDDEN) #JWT 토큰이 만기됨

def putTagData(request):
#     data = TagModel.objects.all()
#     for i in data:
#         temp =  i.searchName.upper()
#         i.searchName = temp
# #         i.save()
#     # json_bookData = dict()
    

    with open("bookky_tagmodel.json","r") as rt_json:
       json_bookData = json.load(rt_json)
    
    # for i in json_bookData:
    #    if i.get('ISBN') is not None:
    #        tempQuery = data.get(Allah_BID = i.get('Allah_BID'))
    #        tempQuery.thumbnail = i.get('thumbnail')
    #        tempQuery.save()

    for i in json_bookData :
        data = {
            'nameTag' : i.get('name'),
            'searchName' : i.get('searchName')
            # 'TBID' : i.get('TBID'),
            # 'TITLE':i.get('TITLE'), 
            # 'SUBTITLE':i.get('SUBTITLE'),
            # 'AUTHOR':i.get('AUTHOR'),
            # 'TAG': i.get('TAG'),
            # 'ISBN':i.get('ISBN'),
            # 'PUBLISHER':i.get('PUBLISHER'),
            # 'PRICE':i.get('PRICE'),
            # 'PAGE':i.get('PAGE') ,
            # 'BOOK_INDEX':i.get('BOOK_INDEX'),
            # 'BOOK_INTRODUCTION':i.get('BOOK_INTRODUCTION'),
            # 'Allah_BID' : int(i.get('Allah_BID')),
            # 'PUBLISH_DATE' : i.get('PUBLISH_DATE'),
            # 'thumbnail' : i.get('thumbnail'),
            # 'RATING' : i.get('RATING'),
            # 'thumbnailImage' : i.get('thumbnailImage'),
            # 'searchName' : i.get('searchName')
        }
        serializer = TagSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)

#     # for i in json_bookData.get('tag'):
#     #     temp = TagModel(
#     #         name = i,
#     #         searchName = i.replace(" ", "")
#     #     )
#     #     temp.save()


#     # for i in json_bookData:
#     #     temp = {'name':i.get('tag'), 'contents':i.get('Elements')}
#     #     serializer = TagSerializer(data = temp)
#     #     if serializer.is_valid() :
#     #         serializer.save()
#     #     else:
#     #         print(serializer.errors)

#     with open("Add_Tag_Book.json","r") as rt_json:
#         json_bookData = json.load(rt_json)


#     bookData = TempBook.objects.all()
#     for i in range(len(json_bookData)):
    
#         Allah_BID = json_bookData[i]["Allah_BID"]
#         Tag = json_bookData[i]["Tag"]
#         print(Allah_BID,Tag)
#         x = bookData.get(Allah_BID = Allah_BID)
#         x.TAG = Tag
#         x.save()

    return JsonResponse({'success':True,'result': 'Gang', 'errorMessage':""}, safe=False, status=status.HTTP_200_OK)    