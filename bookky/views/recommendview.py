from bookky.models import RecommendBook, TempBook, TagModel, User
from bookky.serializers.recommendserializers import RecommendPostSerializer
from bookky.serializers.bookserializers import BookGetSerializer
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg import openapi
import pandas as pd
import numpy as np
import random
def recommendBookCBD(request):
    tagData = TagModel.objects.all()
    data = list()
    for i in tagData:
        data.append(i.TMID)
    tagMatrix = pd.DataFrame(data)
    for i in tagData:
        tagMatrix[i.TMID-1] = 0
    tagMatrix[2][2] = 1

    
    # data = list  = [ 1,2,3 ... 127]
    # tagMatrix[]
    # index 전체 -1 로 잡았음 .
    
    for i in range(len(tagData)):
        Book = TempBook.objects.filter(TAG__contains=[str(i+1)])
        if len(Book) <= 30:
            continue
        for j in range(len(tagData)):
            Book2 = Book.filter(TAG__contains=[str(j+1)])
            if i == j:
                tagMatrix[i][j] = 1.000
            elif len(Book) == 0:
                tagMatrix[i][j] = 0.000
            else:
                tagMatrix[i][j] = round(len(Book2)/len(Book), 3)
            #tagMatrix[i][j] = len(Book2)
        
    tagMatrix.to_csv("tag_similarity.csv", mode='w')

    return JsonResponse({"success":str(tagMatrix)})


# @swagger_auto_schema(
#     method='get',
#     operation_description= "사용자ID 넣기",
#     manual_parameters=[
#         openapi.Parameter('access-token', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='회원이라면 토큰 넣고 비회원이면 넣지 않는다.'),
#         openapi.Parameter('UID', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='사용자ID'),
#     ],
#     responses={
#         200: openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
#                 'result': openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'a' : openapi.Schema('결과', type=openapi.TYPE_STRING)
#                     }
#                 ),
#                 'errorMessage':openapi.Schema('에러메시지', type=openapi.TYPE_STRING),
#             }
#         )
#     }
# )


# @api_view(['GET'])
def metauserfavorite(request):
    if request.method == 'GET' and request.GET.get('UID') is not None:
        # 유저 정보 불러오기
        userID = int(request.GET.get('UID'))
        userdata = User.objects.get(UID = userID)
        
        usertag = userdata.tag_array
        nickname = str(userdata.nickname)

        tag_similarity= pd.read_csv("tag_similarity.csv").values
        n = len(tag_similarity)
        tag_similarity = np.delete(tag_similarity, 0, axis = 1)

        tagdata = np.zeros(n)

        for i in usertag:  
            tagdata += tag_similarity[i-1]
                
        
        temptagdata = tagdata.tolist()
        
        tagdata = [ [temptagdata[i],i+1] for i in range(n) ]
        tagdata.sort(key=lambda x: -x[0])

        metatag = list()
        metatag2 = list()
        
        for i in range(6):
            metatag.append(tagdata[i][1])
        
        for i in range(6):
            metatag2.append(TagModel.objects.get(TMID = tagdata[i][1]).nameTag)

        # meta tag 구하기 끝.
        
        
        bookdata = set()
        temptag = [metatag[0],metatag[1],metatag[2],metatag[3],metatag[4],metatag[5]]
        tempdata = TempBook.objects.filter(TAG__contains= temptag)
        tempser = BookGetSerializer(tempdata,many=True) 
        for x in tempser.data:
            bookdata.add(x["TBID"])

        print("6개 갯수 = ",len(bookdata))
        # tag 6개
        
        if len(bookdata) < 10:
            temptag = [metatag[0],metatag[1],metatag[2],metatag[3],metatag[4],metatag[5]]
            for i in range(6):
                temptag.remove(metatag[i])
                tempdata = TempBook.objects.filter(TAG__contains= temptag )
                tempser = BookGetSerializer(tempdata,many=True) 
                #bookdata.add(tempser.data)
                for x in tempser.data:
                    bookdata.add(x["TBID"])
                temptag.append(metatag[i])
        
            print("5,6개 갯수 = ",len(bookdata))
            # tag 5 개
        
        if len(bookdata) < 10:
            temptag = [metatag[0],metatag[1],metatag[2],metatag[3],metatag[4],metatag[5]]
            for i in range(6):
                temptag.remove(metatag[i])
                for j in range(6):
                    if i == j:
                        continue
                    temptag.remove(metatag[j])
                    #print(temptag)
                    tempdata = TempBook.objects.filter(TAG__contains= temptag )
                    tempser = BookGetSerializer(tempdata,many=True) 
                    #bookdata.add(tempser.data)
                    for x in tempser.data:
                        bookdata.add(x["TBID"])
                    temptag.append(metatag[j])
                temptag.append(metatag[i])  
            print("4,5,6개 갯수 = ",len(bookdata))
        

        RBID = list(bookdata)
        if len(RBID) >= 4:
            RBID = random.sample(RBID,4)

        bookdata = list()
        for i in RBID:
            tempdata = TempBook.objects.get(TBID = i)
            tempser = BookGetSerializer(tempdata)
            bookdata.append(tempser.data)

        
        return JsonResponse({
            'success':True,
            'result' :{"nickname": nickname, "metaTag":metatag2, "bookdata":bookdata},
            'errorMessage':""
            },            status=status.HTTP_200_OK) 
        

def todayRecommendBooks(uid):
    userdata = User.objects.get(UID = uid)
    
    usertag = userdata.tag_array
    nickname = str(userdata.nickname)
    tag_similarity= pd.read_csv("tag_similarity.csv").values
    n = len(tag_similarity)
    tag_similarity = np.delete(tag_similarity, 0, axis = 1)
    tagdata = np.zeros(n)
    for i in usertag:  
        tagdata += tag_similarity[i-1]
            
    
    temptagdata = tagdata.tolist()
    
    tagdata = [ [temptagdata[i],i+1] for i in range(n) ]
    tagdata.sort(key=lambda x: -x[0])
    metatag = list()
    metatag2 = list()
    
    for i in range(6):
        metatag.append(tagdata[i][1])
    
    for i in range(6):
        metatag2.append(TagModel.objects.get(TMID = tagdata[i][1]).nameTag)
    # meta tag 구하기 끝.
    
    
    bookdata = set()
    temptag = [metatag[0],metatag[1],metatag[2],metatag[3],metatag[4],metatag[5]]
    tempdata = TempBook.objects.filter(TAG__contains= temptag)
    tempser = BookGetSerializer(tempdata,many=True) 
    for x in tempser.data:
        bookdata.add(x["TBID"])
    print("6개 갯수 = ",len(bookdata))
    # tag 6개
    
    if len(bookdata) < 10:
        temptag = [metatag[0],metatag[1],metatag[2],metatag[3],metatag[4],metatag[5]]
        for i in range(6):
            temptag.remove(metatag[i])
            tempdata = TempBook.objects.filter(TAG__contains= temptag )
            tempser = BookGetSerializer(tempdata,many=True) 
            #bookdata.add(tempser.data)
            for x in tempser.data:
                bookdata.add(x["TBID"])
            temptag.append(metatag[i])
    
        print("5,6개 갯수 = ",len(bookdata))
        # tag 5 개
    
    if len(bookdata) < 10:
        temptag = [metatag[0],metatag[1],metatag[2],metatag[3],metatag[4],metatag[5]]
        for i in range(6):
            temptag.remove(metatag[i])
            for j in range(6):
                if i == j:
                    continue
                temptag.remove(metatag[j])
                #print(temptag)
                tempdata = TempBook.objects.filter(TAG__contains= temptag )
                tempser = BookGetSerializer(tempdata,many=True) 
                #bookdata.add(tempser.data)
                for x in tempser.data:
                    bookdata.add(x["TBID"])
                temptag.append(metatag[j])
            temptag.append(metatag[i])  
        print("4,5,6개 갯수 = ",len(bookdata))
    
    RBID = list(bookdata)
    if len(RBID) >= 4:
        RBID = random.sample(RBID,4)
    bookdata = list()
    for i in RBID:
        tempdata = TempBook.objects.get(TBID = i)
        tempser = BookGetSerializer(tempdata)
        bookdata.append(tempser.data)
        
    return bookdata
    # 유저 태그 


    # tag_similarity.csv 불러오기


    # meta tag [4개] 계산


    # M.T 기반으로 책 20권


    #142개를 불러온다.
    #아니요, 아닐겁니다의 답변을 받은 태그는 완전히 소거한다.
    #예, 그럴겁니다 답변
    # 태그 142개를 랜덤으로 호출해서 하나씩 질문을 던진다. "{태그}와 관련 있습니까?"
    # 아닙니다., 아닐겁니다. -> 태그 배열에서 아이템 삭제 -> 삭제 배열에 넣음
    # 예 -> 태그 배열에 넣음 (확정 태그 배열에)
    # 그럴겁니다 -> 대기 태그 배열에 넣음
    # "예" 답변이 나오면 바로 책을 조회함
    # 책배열의 아이템 하나씩 책이 가지고 있는 태그를 가져옴 -> 예상 태그 배열에 넣음 -> 삭제 배열과 비교해서 중복되는 부분은 삭제함
    # 예상 태그 배열에 있는 태그를 가져와서 질문을 던짐
    # 위 시퀀스 반복
    # 확정 태그 배열에 요소가 5개를 넘어가면 책 조회 시작
    # 확정 태그 배열에 책을 5개가 매칭 되는 책부터 조회 -> 없으면 4개 -> 없으면 3개 -> 없으면 2개
    # 만약 책 배열의 요소가 10개를 넘어가면 예상 태그 배열에 있는 태그를 가지고 있는 책을 우선적으로 출력함
    # 책 데이터를 넘김 -> 아니라고 답변하면 전체태그 - 확정태그 - 예상태그 - 삭제태그의 결과값에서 태그를 가져와서 다시 질문을 던짐
    # 태그가 10개가 넘어가면 다시 결과 도출 시나리오 시작 