from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from pathlib import Path
from time import sleep
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg import openapi
import base64
from bookky.serializers.userserializers import UserRegisterSerializer
from bookky.models import User, RefreshTokenStorage, Tag
from bookky.auth.auth import setToken, get_access, checkToken, get_refreshToken, re_generate_Token, getAuthenticate, checkAuthentication, checkAuth_decodeToken
from bookky_backend import settings
import os

# @api_view(['POST'])
# def fileUpload(request):
#     if request.method == 'POST':
#         title = request.POST['imageTitle']
#         content = request.POST['content']
#         img = request.FILES["imageFile"]
#         fileupload = ImageStorage(
#             imageTitle=title,
#             content=content,
#             imageFile=img,
#         )
#         print(fileupload)
#         print(type(img))
#         fileupload.save()

        

#         return JsonResponse({"success":True})



@api_view(['POST'])
def userThumbnailPost(request):
    flag = checkAuth_decodeToken(request)
    # exceptDict = {'BID' : 0, 'UID':0}
    exceptDict = None
    if flag == 0:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    elif flag == 1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == 2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)
    
    if request.method == 'POST':
        userQuery = User.objects.get(UID = int(flag))
        if request.FILES is not None:
            userQuery.imageFile = request.FILES["imageFile"]
            userQuery.thumbnail = "http://203.255.3.144:8010/thumbnail/userThumbnail/"+str(userQuery.email)+'/'+str(request.FILES[u'imageFile'].name)
            userQuery.save()
            return JsonResponse({'route':"http://203.255.3.144:8010/thumbnail/userThumbnail/"+str(userQuery.email)+'/'+str(request.FILES[u'imageFile'].name)})
        else:
            return JsonResponse({'success':False})


def decodeBase64(encodedImage, path):
    header, data = encodedImage.split(';base64,') #base64형태는 data:image/png;base64,로 시작함 즉 파일 형태와 파일 확장자가 앞에 붙음 이걸 이미지로 디코딩하면 깨져버리기 때문에 분할 해줘야함
    data_format, ext = header.split('/') #data타입과 확장자 분리함
    # imageArray = [] #만약에 다수의 이미지가 넘어오면 리턴타입도 복수로 바꿔주는게?
    print(encodedImage)
    # num = 0
    try:
        # for image_string in self.context.get("images"):
        image_data = base64.b64decode(data)
        image_root = settings.MEDIA_ROOT+'/thumbnail/' + path + "thumbnail" + "." + ext
        imagesname = "thumbnail" + "." + ext
        with open(image_root, 'wb') as f:
            f.write(image_data)
        # num += 1
            # imageArray.append(image_data)
    except TypeError:
        self.fail('invalid_image')

    return imagesname