from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from .models import Book
from .bookserializers import BookPostSerializer

import requests
import datetime
import urllib.request
import json
import time

def saveAPIDatafromCrawl():
    #crawlling 해서 나온 데이터를 정의
    crawlData = {}
    jsonData = JSONParser().parse(crawlData)
    parseSerializer = BookPostSerializer(data = jsonData) #BookPostSerializer 양식에 맞춰서 데이터를 넣어야함
    if parseSerializer.is_valid():
        parseSerializer.save()
        return JsonResponse({'success':True, 'result':parseSerializer.data}, status = status.HTTP_201_CREATED)
    else:
        print(request.body)
        print(parseSerializer.errors)
        return JsonResponse({'success':False, 'result':{}, status = status.HTTP_400_BAD_REQUEST})