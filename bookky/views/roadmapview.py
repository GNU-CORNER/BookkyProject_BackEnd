from bookky.auth.auth import checkAuth_decodeToken
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from django.db.models import Q
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg import openapi


@api_view(['GET'])
def getRoadmapData(request):
    if request.method == 'GET':
        Data = {1:[],2:[]} #딕셔너리에 2중 배열이 담긴 형태로 데이터 설정 그래서 전체 데이터 셋에서 '키'형태로
        courseType = int(request.GET.get('type')) #1번은 Front-End, 2번은 Back-End, 3번은 아직 미정
        
        
    