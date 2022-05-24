from bookky.models import FavoriteBook, User, AnyCommunity, QnACommunity, MarketCommunity, TagModel, TempBook, QnAComment, MarketComment, AnyComment, Review
from bookky.serializers.favoriteserializers import FavoriteBookSerializer
from bookky.serializers.bookserializers import BookPostSerializer, BookGetSerializer
from bookky.serializers.tagserializers import TagSerializer
from bookky.serializers.communityserializers import AnyCommunitySerializer, QnACommunitySerializer, MarketCommunitySerializer
from bookky.serializers.reviewserializers import ReviewGetSerializer
from bookky.views.uploadView import decodeBase64
from bookky.auth.auth import checkAuth_decodeToken

from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from django.db.models import Q
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
    operation_description="사용자 관심도서 출력 : pk에 0값을 넣어 호출",
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'favoriteBookList' : openapi.Schema('사용자가 선택한 태그', type=openapi.TYPE_ARRAY, items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'TBID' : openapi.Schema('TBID', type=openapi.TYPE_INTEGER),
                                'TITLE' : openapi.Schema('책 제목', type=openapi.TYPE_STRING),
                                'thumbnailImage' : openapi.Schema('책 사진', type=openapi.TYPE_STRING),
                            }
                        )
                        )
                        
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)

@swagger_auto_schema(
    method='post',
    operation_description="관심도서 등록 : pk에 BID값을 넣어 호출",
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
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
                                'isFavorite' : openapi.Schema('관심도서인지?', type=openapi.TYPE_BOOLEAN),
                            }
                        )
                        
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
@api_view(['GET','POST'])
def favoriteBook(request, pk): #관심 도서 등록 및 취소
    flag = checkAuth_decodeToken(request)
    print(flag)
    # exceptDict = {'BID' : 0, 'UID':0}
    exceptDict = None
    if flag == 0:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    elif flag == -1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == -2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)
    

    if request.method == 'GET':
        data = list()
        tempQuery = FavoriteBook.objects.filter(UID = flag)
        if len(tempQuery) != 0:
            for i in tempQuery:
                bookQuery = TempBook.objects.get(TBID = i.TBID.TBID)
                tempData = {'TBID':i.TBID.TBID, 'TITLE':bookQuery.TITLE, 'thumbnailImage':bookQuery.thumbnailImage}
                data.append(tempData)
            return JsonResponse({'success':True, 'result':{'favoriteBookList':data}, 'errorMessage':""}, status = status.HTTP_200_OK)
        else:
            return JsonResponse({'success':True, 'result':{'favoriteBookList':data}, 'errorMessage':""}, status = status.HTTP_204_NO_CONTENT)

    elif request.method == 'POST':
        data = dict()
        data['TBID'] = pk
        data['UID'] = flag
        queryData = FavoriteBook.objects.filter(UID = flag)
        queryData = queryData.filter(TBID = pk)
        if len(queryData) == 0 :
            serializer = FavoriteBookSerializer(data =data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'success':True, 'result':{'isFavorite':True}, 'errorMessage':""}, status = status.HTTP_200_OK)
            else:
                return JsonResponse({'success':False, 'result':{'isFavorite':False}, 'errorMessage':serializer.errors}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            queryData.delete()
            return JsonResponse({'success':True, 'result':{'isFavorite':False}, 'errorMessage':""}, status = status.HTTP_200_OK)
        
@swagger_auto_schema(
    method='get',
    operation_description="프로필 화면 데이터 출력",
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="꼭 넣어야함. 비회원은 로그인 페이지로 넘어가게 만들기", type=openapi.TYPE_STRING)],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'userData': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'nickname':openapi.Schema('사용자 닉네임',type=openapi.TYPE_STRING),
                                'thumbnail':openapi.Schema('사용자 프로필 사진', type=openapi.TYPE_STRING),
                                'tag_array':openapi.Schema(
                                    '태그이름',
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Items(type=openapi.TYPE_STRING)
                                )
                            }
                        ),
                        'favoriteBookList' : openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'TBID':openapi.Schema('TBID', type=openapi.TYPE_INTEGER),
                                    'TITLE':openapi.Schema('책 제목', type=openapi.TYPE_STRING),
                                    'AUTHOR':openapi.Schema('책 저자', type=openapi.TYPE_STRING),
                                    'thumbnailImage':openapi.Schema('책 이미지', type=openapi.TYPE_STRING),
                                }
                            )
                        ),    
                        'userPostList' : openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'PID':openapi.Schema('포스트 번호', type=openapi.TYPE_INTEGER),
                                    'title':openapi.Schema('게시글 제목', type=openapi.TYPE_STRING),
                                    'contents':openapi.Schema('게시글 내용', type=openapi.TYPE_STRING),
                                    'communityType':openapi.Schema('게시판종류', type=openapi.TYPE_INTEGER),
                                    'commentCnt':openapi.Schema('댓글 개수', type=openapi.TYPE_INTEGER),
                                    'likeCnt':openapi.Schema('좋아요 개수', type=openapi.TYPE_INTEGER),
                                }
                            )
                        ),
                        'userReviewList': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'RID':openapi.Schema('RID', type=openapi.TYPE_INTEGER),
                                'TBID':openapi.Schema('TBID', type=openapi.TYPE_INTEGER),
                                'UID':openapi.Schema('UID', type=openapi.TYPE_INTEGER),
                                'contents':openapi.Schema('게시글 내용', type=openapi.TYPE_STRING),
                                'views':openapi.Schema('views', type=openapi.TYPE_INTEGER),
                                'createAt':openapi.Schema('작성날짜', type=openapi.TYPE_STRING),
                                'rating': openapi.Schema('리뷰 평점', type=openapi.TYPE_INTEGER),
                                'likeCnt':openapi.Schema('좋아요 개수', type=openapi.TYPE_INTEGER),
                                'isLiked':openapi.Schema('이글에 좋아요를 했는지?', type=openapi.TYPE_BOOLEAN),
                                'isAccessible':openapi.Schema('이글에 접근이 가능한지?', type=openapi.TYPE_BOOLEAN),
                                'nickname':openapi.Schema('사용자 이름', type=openapi.TYPE_STRING),
                                'AUTHOR':openapi.Schema('책 저자', type=openapi.TYPE_STRING),
                                'bookTitle':openapi.Schema('책 제목', type=openapi.TYPE_STRING),
                                'thumbnail':openapi.Schema('책 사진', type=openapi.TYPE_STRING),
                            }
                        )
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)   
#마이페이지 출력 (관심도서 출력, 사용자 정보, 사용자 게시글, 사용자 후기, 사용자 관심분야)
@api_view(['GET'])
def getMyProfileData(request):
    exceptDict = None
    returnDict = dict()
    if request.method == 'GET':
        flag = checkAuth_decodeToken(request)
        if flag == 0:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
        elif flag == -1:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
        elif flag == -2:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)
        else:
            tagQuery = TagModel.objects
            userTag = []
            userQuery = User.objects.get(UID = flag)
            if userQuery.tag_array is not None:
                for i in userQuery.tag_array:
                    temp = tagQuery.get(TMID=i)
                    userTag.append({'tag':temp.nameTag, 'TMID':temp.TMID})    
            userData = {'userThumbnail':userQuery.thumbnail,'nickname':userQuery.nickname, 'userTagList':userTag}
            bookQuery = FavoriteBook.objects.filter(UID = int(flag))
            bookQueryList = FavoriteBookSerializer(bookQuery, many=True)
            bookList = []
            for i in bookQueryList.data:
                dataQuery = TempBook.objects.filter(TBID = i['TBID'])
                tempBookQuery = BookGetSerializer(dataQuery, many = True)
                bookList += tempBookQuery.data
            tempAnyCommunityData = AnyCommunity.objects.order_by('createAt').filter(UID = flag)
            tempQnACommunityData = QnACommunity.objects.order_by('createAt').filter(UID = flag)
            tempMarketCommunityData = MarketCommunity.objects.order_by('createAt').filter(UID = flag)

            anySerializer = AnyCommunitySerializer(tempAnyCommunityData, many=True)
            qnaSerializer = MarketCommunitySerializer(tempQnACommunityData, many=True)
            marketSerializer = QnACommunitySerializer(tempMarketCommunityData, many=True)
            
            anyList = anySerializer.data
            qnaList = qnaSerializer.data
            marketList = marketSerializer.data

            anyCommunityList = comment_like_counter("0", anyList)
            qnaCommunityList = comment_like_counter("1",qnaList)
            marketCommunityList = comment_like_counter("2",marketList)

            community = anyCommunityList + qnaCommunityList + marketCommunityList
            # community = []
            # community.append(anyCommunityList)
            # community.append(qnaCommunityList)
            # community.append(marketCommunityList)
            reviewQuery = Review.objects.order_by('createAt').filter(UID = flag)
            reviewSerializer = ReviewGetSerializer(reviewQuery, many=True)
            for i in reviewSerializer.data:
                temp = User.objects.get(UID=i['UID'])
                i['likeCnt'] = len(i['like'])
                if i['like'].count(flag) > 0:
                    i['isLiked'] = True
                else:
                    i['isLiked'] = False
                del i['like']
                i['isAccessible'] = True
                i['nickname'] = temp.nickname
                tempQuery = TempBook.objects.get(TBID = i['TBID'])
                i['AUTHOR'] = tempQuery.AUTHOR
                i['bookTitle'] = tempQuery.TITLE
                i['thumbnail'] = tempQuery.thumbnailImage
            returnDict = {'userData':userData,'favoriteBookList':bookList, 'userPostList':community,'userReviewList':reviewSerializer.data}

            return JsonResponse({'success':True, 'result':returnDict, 'errorMessage':""}, status = status.HTTP_200_OK)

def comment_like_counter(flag, dataList):
    tempList = []
    for i in dataList:
        if flag == "0":
            commentData = AnyComment.objects.filter(APID = i['APID'])
            i['communityType'] = 0
            i['PID'] = i['APID']
            del i['APID']
        elif flag == "1":
            commentData = QnAComment.objects.filter(QPID = i['QPID'])
            i['communityType'] = 1
            i['PID'] = i['QPID']
            del i['QPID']
        elif flag =="2":
            commentData = MarketComment.objects.filter(MPID = i['MPID'])
            i['communityType'] = 2
            i['PID'] = i['MPID']
            del i['MPID']
        if len(commentData) !=0:
            i['commentCnt'] = len(commentData)
        else:
            i['commentCnt'] = 0
        if len(i['like']) !=0:
            i['likeCnt'] = len(i['like'])
        else:
            i['likeCnt'] = 0
        del i['like']
        tempList.append(i)
    return tempList

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
                                    'TMID' : openapi.Schema('태그 아이디', type=openapi.TYPE_INTEGER),
                                    'data' :openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Items(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'TBID':openapi.Schema('TBID', type=openapi.TYPE_INTEGER),
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
                                'tagData':openapi.Schema(
                                    '태그이름',
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Items(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                        'tag' : openapi.Schema('태그이름',type=openapi.TYPE_STRING),
                                        'TMID' : openapi.Schema('태그 아이디', type=openapi.TYPE_INTEGER),
                                        }
                                        )
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
            bookQuery = TempBook.objects
            tagQuery = TagModel.objects
            bookList = [{'tag':"오늘의 추천 도서", 'data':[]}]
            userData = dict()
        except:
            return JsonResponse({'success':False, 'result':{}, 'errorMessage':"DB와 연결 끊김"},status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        userStack = [1,19, 29]
        if request.headers.get('access_token', None) is not None: #회원일 때
            if len(request.headers.get('access_token', None)) != 0:
                flag = checkAuth_decodeToken(request)
                print(flag)
                if flag == -1:
                    return JsonResponse({'success':False, 'result':{'bookList':exceptDict,'communityList':[],'userData':None}, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
                elif flag == -2:
                    return JsonResponse({'success':False, 'result':{'bookList':exceptDict,'communityList':[],'userData':None}, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)
                userQuery = User.objects.get(UID = flag)
                userData['UID'] = int(userQuery.UID)
                tempTag = []
                userTag = userQuery.tag_array
                if userTag is None:
                    userData['tagData'] = []
                else:
                    userStack = userTag
                for i in userStack:
                    temp = tagQuery.get(TMID=i)
                    tempTag.append({'TMID' : i,'tag':temp.nameTag})
                userData['tagData'] = tempTag
                userData['nickname'] = userQuery.nickname
                userData['thumbnail'] = userQuery.thumbnail
        
        for i in userStack:
            temp = tagQuery.get(TMID = i)
            bookTemp = bookQuery.filter(TAG__contains = [i])
            serializer = BookGetSerializer(bookTemp, many=True)
            tempSpiltData = serializer.data
            bookList.append({'tag':temp.nameTag, 'TMID':i, 'data':tempSpiltData[0:25]})
        
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
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST, safe=False)
        elif flag == -1:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN, safe=False)
        elif flag == -2:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED, safe=False)
        else:
            if data['tag'] is not None and len(data['tag']) != 0:
                tagQuery = TagModel.objects
                for i in data['tag']:
                    if tagQuery.get(TMID = int(i)) is None:
                        errorFlag = True
                        break
                if errorFlag:
                    return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"존재하지 않는 태그 값"}, status = status.HTTP_400_BAD_REQUEST, safe=False)
                userData = User.objects.get(UID=int(flag))
                userData.tag_array = data['tag']
                userData.save()
                tempTag = []
                for i in userData.tag_array:
                    temp = tagQuery.get(TMID=i)
                    tempTag.append(temp.nameTag)

                return JsonResponse({'success':True, 'result':{'tag':tempTag}, 'errorMessage':""},status = status.HTTP_200_OK, safe=False)
            else:
                return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"Body에 태그 값이 없습니다"}, status = status.HTTP_400_BAD_REQUEST, safe=False)


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
                                'TMID':openapi.Schema('TMID', type=openapi.TYPE_INTEGER),
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
        tags = TagModel.objects.all()
        dataset = TagSerializer(tags, many=True)
        temp = dataset.data
        
        return JsonResponse({'success':True, 'result':{'tag':temp}, 'errorMessage':""},status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="main 화면 태그 더보기 데이터 출력",
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
                                    'TMID' : openapi.Schema('태그 아이디', type=openapi.TYPE_INTEGER),
                                    'data' :openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Items(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'TBID':openapi.Schema('TBID', type=openapi.TYPE_INTEGER),
                                                'TITLE':openapi.Schema('책 제목', type=openapi.TYPE_STRING),
                                                'AUTHOR':openapi.Schema('책 저자', type=openapi.TYPE_STRING),
                                                'thumbnailImage':openapi.Schema('책 이미지', type=openapi.TYPE_STRING),
                                            }
                                        )
                                    )
                                    
                                }
                            )
                        ),
                        'nickname' : openapi.Schema('닉네임',type=openapi.TYPE_STRING),
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)   
@api_view(['GET'])
def getMoreTag(request):
    if request.method == 'GET':

        exceptDict = None
        try:
            bookQuery = TempBook.objects
            tagQuery = TagModel.objects
            bookList = [{'tag':"오늘의 추천 도서", 'data':[]}]
            nickname = "비회원"
        except:
            return JsonResponse({'success':False, 'result':{'bookList':exceptDict,'nickname':exceptDict}, 'errorMessage':"DB와 연결 끊김"},status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        userStack = [1,19, 29]
        if request.headers.get('access_token', None) is not None: #회원일 때
            if len(request.headers.get('access_token', None)) != 0:
                flag = checkAuth_decodeToken(request)
                if flag == -1:
                    return JsonResponse({'success':False, 'result':{'bookList':exceptDict,'nickname':exceptDict}, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
                elif flag == -2:
                    return JsonResponse({'success':False, 'result':{'bookList':exceptDict,'nickname':exceptDict}, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)
                userQuery = User.objects.get(UID = flag)

                tempTag = []
                userTag = userQuery.tag_array
                if userTag is not None:
                    userStack = userTag
                for i in userStack:
                    temp = tagQuery.get(TMID=i)
                    tempTag.append({'TMID' : i,'tag':temp.nameTag})
                nickname = userQuery.nickname
        
        for i in userStack:
            temp = tagQuery.get(TMID = i)
            bookTemp = bookQuery.filter(TAG__contains = [i])
            serializer = BookGetSerializer(bookTemp, many=True)
            tempSpiltData = serializer.data
            bookList.append({'tag':temp.nameTag, 'TMID':i, 'data':tempSpiltData[0:25]})
        
        return JsonResponse({'success':True,'result' :{'bookList':bookList,'nickname':nickname},'errorMessage':""},status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='put',
    operation_description="사용자 이미지, 닉네임 수정",
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'nickname' : openapi.Schema('수정할 닉네임', type=openapi.TYPE_STRING),
            'images' : openapi.Schema('수정할 이미지 base64', type=openapi.TYPE_STRING)
        },
        required=['contents', 'rating']
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
@api_view(['PUT'])
def updateUserProfile_nickname(request):
    flag = checkAuth_decodeToken(request)
    # exceptDict = {'BID' : 0, 'UID':0}
    exceptDict = None
    if flag == 0:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    elif flag == -1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == -2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)
    
    if request.method == 'PUT':
        parseData = JSONParser().parse(request)
        userQuery = User.objects.get(UID = int(flag))
        
        if len(parseData['nickname']) > 1 and parseData['nickname'] is not None:
            imagesname = decodeBase64(parseData['images'], "userThumbnail/"+str(userQuery.email)+'/')
            userQuery.nickname = parseData['nickname']
            userQuery.thumbnail = "http://203.255.3.144:8010/thumbnail/userThumbnail/"+str(userQuery.email)+'/'+imagesname
            userQuery.save()
            return JsonResponse({'route':"http://203.255.3.144:8010/thumbnail/userThumbnail/"+str(userQuery.email)+'/'+imagesname, 'nickname': parseData['nickname']},status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False})

@swagger_auto_schema(
    method='get',
    operation_description="사용자의 리뷰를 가져오는 API",
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "reviewList": openapi.Schema('책의 리뷰리스트', type=openapi.TYPE_ARRAY, items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'RID':openapi.Schema('RID', type=openapi.TYPE_INTEGER),
                                'TBID':openapi.Schema('TBID', type=openapi.TYPE_INTEGER),
                                'UID':openapi.Schema('UID', type=openapi.TYPE_INTEGER),
                                'contents':openapi.Schema('게시글 내용', type=openapi.TYPE_STRING),
                                'views':openapi.Schema('views', type=openapi.TYPE_INTEGER),
                                'createAt':openapi.Schema('작성날짜', type=openapi.TYPE_STRING),
                                'rating': openapi.Schema('리뷰 평점', type=openapi.TYPE_INTEGER),
                                'likeCnt':openapi.Schema('좋아요 개수', type=openapi.TYPE_INTEGER),
                                'isLiked':openapi.Schema('이글에 좋아요를 했는지?', type=openapi.TYPE_BOOLEAN),
                                'isAccessible':openapi.Schema('이글에 접근이 가능한지?', type=openapi.TYPE_BOOLEAN),
                                'nickname':openapi.Schema('사용자 이름', type=openapi.TYPE_STRING),
                                'AUTHOR':openapi.Schema('책 저자', type=openapi.TYPE_STRING),
                                'bookTitle':openapi.Schema('책 제목', type=openapi.TYPE_STRING),
                                'thumbnail':openapi.Schema('책 사진', type=openapi.TYPE_STRING),
                            })
                        )
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
@api_view(['GET'])
def getUserReview(request):
    flag = checkAuth_decodeToken(request)
    # exceptDict = {'BID' : 0, 'UID':0}
    exceptDict = None
    if flag == 0:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    elif flag == -1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == -2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)
    
    if request.method =='GET':
        reviewQuery = Review.objects.filter(UID=flag)
        if len(reviewQuery) != 0:
            serializers = ReviewGetSerializer(reviewQuery, many=True)
            for i in serializers.data:
                i['likeCnt'] = len(i['like'])
                if i['like'].count(flag) > 0:
                    i['isLiked'] = True
                else:
                    i['isLiked'] = False
                del i['like']
                if int(i['UID']) == int(flag):
                    i['isAccessible'] = True
                else:
                    i['isAccessible'] = False
                temp = User.objects.get(UID=i['UID'])
                i['nickname'] = temp.nickname
                tempQuery = TempBook.objects.get(TBID = i['TBID'])
                i['AUTHOR'] = tempQuery.AUTHOR
                i['bookTitle'] = tempQuery.TITLE
                i['thumbnail'] = tempQuery.thumbnailImage
            return JsonResponse({'success':True, 'result':{'reviewList':serializers.data}, 'errorMessage':""}, status = status.HTTP_200_OK)
        else:
            return JsonResponse({'success':True, 'result':{'reviewList':exceptDict},'errorMessage':""},status=status.HTTP_204_NO_CONTENT)