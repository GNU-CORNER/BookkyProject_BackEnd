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

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def book(request):   