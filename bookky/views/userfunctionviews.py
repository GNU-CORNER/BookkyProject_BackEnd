from bookky.models import FavoriteBook, User, AnyCommunity, QnACommunity, MarketCommunity, Tag, Book
from bookky.serializers.favoriteserializers import FavoriteBookSerializer
from bookky.serializers.bookserializers import BookPostSerializer, BookGetSerializer
from bookky.serializers.tagserializers import TagSerializer
from bookky.auth.auth import checkAuth_decodeToken

from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from django.db.models import Q
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg import openapi

#관심 도서 등록
@swagger_auto_schema(
    method='delete',
    operation_description="관심도서 삭제",
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'BID': openapi.Schema('도서ID', type=openapi.TYPE_INTEGER),
        },
        required=['BID']  # 필수값을 지정 할 Schema를 입력해주면 된다.
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
@swagger_auto_schema(
    method='post',
    operation_description="관심도서 등록",
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'BID': openapi.Schema('도서ID', type=openapi.TYPE_INTEGER),
        },
        required=['BID']  # 필수값을 지정 할 Schema를 입력해주면 된다.
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'favoriteItem' : openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'BID' : openapi.Schema('책 ID', type=openapi.TYPE_INTEGER),
                                'UID' : openapi.Schema('사용자 ID', type=openapi.TYPE_INTEGER),
                            }
                        )
                        
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
@api_view(['POST', 'DELETE'])
def favoriteBook(request): #관심 도서 등록 및 취소
    data = JSONParser().parse(request)
    flag = checkAuth_decodeToken(request)
    # exceptDict = {'BID' : 0, 'UID':0}
    exceptDict = None
    if flag == 0:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    elif flag == 1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == 2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_403_FORBIDDEN)
    
    if request.method == 'POST':
        if data['BID'] is not None:
            data['UID'] = flag
            queryData = FavoriteBook.objects.filter(UID = flag)
            queryData = queryData.filter(BID = data['BID'])
            if len(queryData) == 0 :
                serializer = FavoriteBookSerializer(data =data)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse({'success':True, 'result':{'favoriteItem':serializer.data}, 'errorMessage':""}, status = status.HTTP_200_OK)
                else:
                    return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':serializer.errors}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"이미 추가되어 있습니다."},status = status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"Body에 BID값이 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if data['BID'] is not None:
            queryData = FavoriteBook.objects.filter(UID = flag)
            queryData = queryData.filter(BID = data['BID'])
            if len(queryData) != 0:
                queryData.delete()
                return JsonResponse({'success':True, 'result':exceptDict, 'errorMessage':""}, status = status.HTTP_200_OK)
            else:
                return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"해당 책을 관심 도서로 등록하지 않았습니다."}, status = status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"Body에 BID값이 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
        

#마이페이지 출력 (관심도서 출력, 사용자 정보, 사용자 게시글, 사용자 후기, 사용자 관심분야)
@api_view(['GET'])
def getMyProfileData(request):
    if request.method == 'GET':
        flag = checkAuth_decodeToken(request)
        if flag == 0:
            return JsonResponse({'success':False, 'result':{}, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
        elif flag == 1:
            return JsonResponse({'success':False, 'result':{}, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
        elif flag == 2:
            return JsonResponse({'success':False, 'result':{}, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_403_FORBIDDEN)
        else:
            userQuery = User.objects.get(UID = flag)
            bookQuery = FavoriteBook.objects.filter(UID = flag)
            community = [{'communityName':"자유게시판", 'posts':[]},{'communityName':"QnA게시판", 'posts':[]},{'communityName':"장터게시판", 'posts':[]}]
            tempAnyCommunityData = AnyCommunity.objects.filter(UID = flag)
            tempQnACommunityData = QnACommunity.objects.filter(UID = flag)
            tempMarketCommunityData = MarketCommunity.objects.filter(UID = flag)


            return JsonResponse({'success':True, 'result':{}, 'errorMessage':""}, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="main 화면 데이터 출력",
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="회원이면 넣고, 비회원은 넣지 않는다.", type=openapi.TYPE_STRING)],
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
                        ),
                        'communityList' : openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={}
                            )
                        ),
                        'userData': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'UID' : openapi.Schema('UID', type=openapi.TYPE_INTEGER),
                                'tag_array':openapi.Schema(
                                    '태그이름',
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Items(type=openapi.TYPE_STRING)
                                ),
                                'nickname':openapi.Schema('사용자 닉네임',type=openapi.TYPE_STRING),
                                'thumbnail':openapi.Schema('사용자 프로필 사진', type=openapi.TYPE_STRING)
                            }
                        )
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)   
@api_view(['GET'])
def getHomeData(request):
    if request.method == 'GET':
        # exceptDict = [{'tag':"",'data':[]}]
        exceptDict = None
        try:
            bookQuery = Book.objects
            tagQuery = Tag.objects
            bookList = []
            userData = dict()
        except:
            return JsonResponse({'success':False, 'result':{}, 'errorMessage':"DB와 연결 끊김"},status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        userStack = [1,19, 29]
        if request.headers.get('access_token', None) is not None: #회원일 때
            print(request.headers.get('access_token',None))
            if len(request.headers.get('access_token', None)) != 0:
                flag = checkAuth_decodeToken(request)
                if flag == 1:
                    return JsonResponse({'success':False, 'result':{'bookList':exceptDict,'communityList':[],'userData':None}, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
                elif flag == 2:
                    return JsonResponse({'success':False, 'result':{'bookList':exceptDict,'communityList':[],'userData':None}, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_403_FORBIDDEN)
                userQuery = User.objects.get(UID = flag)
                userData['UID'] = int(userQuery.UID)
                tempTag = []
                userTag = userQuery.tag_array
                if userTag is None:
                    userData['tag_array'] = []
                else:
                    userStack = userTag
                for i in userStack:
                    temp = tagQuery.get(TID=i)
                    tempTag.append(temp.nameTag)
                userData['tag_array'] = tempTag
                userData['nickname'] = userQuery.nickname
                userData['thumbnail'] = userQuery.thumbnail
        
        for i in userStack:
            temp = tagQuery.get(TID = i)
            bookTemp = bookQuery.filter(TAG__contains = [i])
            serializer = BookGetSerializer(bookTemp, many=True)
            tempSpiltData = serializer.data
            bookList.append({'tag':temp.nameTag, 'data':tempSpiltData[0:25]})
        
        return JsonResponse({'success':True,'result' :{'bookList':bookList,'communityList':[],'userData':userData},'errorMessage':""},status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='put',  
    manual_parameters=[
        openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING),
    ],
    request_body=openapi.Schema(
        '해당 내용의 titile',
        type=openapi.TYPE_OBJECT,
        properties={
            'tag' : openapi.Schema('사용자가 선택한 태그', type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))
        },
        required=['email', 'code']  # 필수값을 지정 할 Schema를 입력해주면 된다.
    ),
    # 필수값을 지정 할 Schema를 입력해주면 된다.
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'tag' : openapi.Schema('사용자가 선택한 태그', type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING))
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING),
            }
        )
    }
)    
#관심분야 업데이트
@api_view(['PUT'])
def updateBoundary(request):
    if request.method == 'PUT':
        # exceptDict = {'tag':[]}
        exceptDict = None
        data = JSONParser().parse(request)
        flag = checkAuth_decodeToken(request)
        errorFlag = False
        if flag == 0:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
        elif flag == 1:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
        elif flag == 2:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_403_FORBIDDEN)
        else:
            if data['tags'] is not None and len(data['tags']) != 0:
                tagQuery = Tag.objects
                for i in data['tags']:
                    if tagQuery.get(TID = int(i)) is None:
                        errorFlag = True
                        break
                if errorFlag:
                    return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"존재하지 않는 태그 값"}, status = status.HTTP_400_BAD_REQUEST)
                userData = User.objects.get(UID=int(flag))
                userData.tag_array = data['tags']
                userData.save()
                tempTag = []
                for i in userData.tag_array:
                    temp = tagQuery.get(TID=i)
                    tempTag.append(temp.nameTag)

                return JsonResponse({'success':True, 'result':{'tag':tempTag}, 'errorMessage':""},status = status.HTTP_200_OK)
            else:
                return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"Body에 태그 값이 없습니다"}, status = status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',  
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'tag' : openapi.Schema('태그 데이터', type=openapi.TYPE_ARRAY, items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'TID':openapi.Schema('TID', type=openapi.TYPE_INTEGER),
                                'nameTag':openapi.Schema('태그 이름', type=openapi.TYPE_STRING)
                            }
                        )
                        )
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING),
            }
        )
    }
)    
#태그정보 받기
@api_view(['GET'])
def getTags(request):
    if request.method == 'GET':
        tags = Tag.objects.all()
        dataset = TagSerializer(tags, many=True)
        temp = dataset.data
        for i in range(0,len(temp)):
            del temp[i]['contents']
        
        return JsonResponse({'success':True, 'result':{'tag':temp}, 'errorMessage':""},status=status.HTTP_200_OK)