from bookky.models import Review, TempBook, User
from bookky.serializers.bookserializers import BookPostSerializer, BookGetSerializer
from bookky.serializers.tagserializers import TagSerializer
from bookky.auth.auth import checkAuth_decodeToken
from bookky.serializers.reviewserializers import ReviewPostSerializer, ReviewGetSerializer

from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from django.db.models import Q
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg import openapi
import datetime
#'RID','BID','UID','contents','views','createAt','updateAt','like', 'rating'
@swagger_auto_schema(
    method='post',
    operation_description="리뷰 등록",
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'contents' : openapi.Schema('수정된 후기 내용', type=openapi.TYPE_STRING),
            'rating' : openapi.Schema('수정된 평점', type=openapi.TYPE_INTEGER)
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
@swagger_auto_schema(
    method='get',
    operation_description="가져올 리뷰의 RID를 입력",
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
@swagger_auto_schema(
    method='delete',
    operation_description="삭제할 리뷰의 RID를 ID에 입력",
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
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
    method='put',  
    operation_description="수정할 RID를 ID에 입력",
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'contents' : openapi.Schema('수정된 후기 내용', type=openapi.TYPE_STRING),
            'rating' : openapi.Schema('수정된 평점', type=openapi.TYPE_INTEGER)
        },
        required=['contents', 'rating']
    ),  # 필수값을 지정 할 Schema를 입력해주면 된다.
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'review':openapi.Schema(
                            type = openapi.TYPE_OBJECT,
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
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def reviews(request, pk):
    flag = checkAuth_decodeToken(request)
    exceptDict = None
    if flag == 0:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    elif flag == -1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == -2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET': #리뷰 하나를 특정해서 출력하는 API
        reviewQuery = Review.objects.filter(RID=pk)
        if len(reviewQuery) != 0:
            serializers = ReviewGetSerializer(reviewQuery, many=True)
            for i in serializers.data:
                temp = User.objects.get(UID=i['UID'])
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
                i['nickname'] = temp.nickname
                tempQuery = TempBook.objects.get(TBID = i['TBID'])
                i['AUTHOR'] = tempQuery.AUTHOR
                i['bookTitle'] = tempQuery.TITLE
                i['thumbnail'] = tempQuery.thumbnailImage
            reviewData = serializers.data
            reviewQuery = Review.objects.get(RID=pk)
            reviewQuery.views = reviewQuery.views + 1
            reviewData[0]['views'] = reviewQuery.views
            reviewQuery.save()
            return JsonResponse({'success':True, 'result':{'review':reviewData[0]}, 'errorMessage':""}, status = status.HTTP_200_OK)
        else:
            return JsonResponse({'success':True, 'result':{'review':exceptDict},'errorMessage':"해당 아이디의 리뷰가 존재하지 않습니다."},status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'POST': #리뷰 등록 API
        data = JSONParser().parse(request)
        if data['contents'] is not None:
            data['UID'] = flag
            data['TBID'] = pk
            temp = Review.objects.filter(                    
                Q(TBID = pk) & #책 소개
                Q(UID = flag)
            )
            if len(temp) == 0: 
                serializer = ReviewPostSerializer(data = data)
                if serializer.is_valid():
                    bookQuery = TempBook.objects.get(TBID = pk)
                    reviewCnt = len(Review.objects.filter(TBID = pk))
                    if reviewCnt == 0:
                        tempRating = float(data['rating'])
                    else:
                        tempRating = (float(bookQuery.RATING) * float(reviewCnt) + float(data['rating'])) / (float(reviewCnt) + 1.0)
                    bookQuery.RATING = tempRating
                    bookQuery.save()
                    serializer.save()
                    tempData = serializer.data
                    tempData['likeCnt'] = len(tempData['like'])
                    tempData['isLiked'] = False
                    del tempData['like']
                    tempData['isAccessible'] = True
                    temp = User.objects.get(UID=tempData['UID'])
                    tempData['nickname'] = temp.nickname
                    tempQuery = TempBook.objects.get(TBID = tempData['TBID'])
                    tempData['AUTHOR'] = tempQuery.AUTHOR
                    tempData['bookTitle'] = tempQuery.TITLE
                    tempData['thumbnail'] = tempQuery.thumbnailImage
                    return JsonResponse({'success':True, 'result':{'review':tempData}, 'errorMessage':""}, status = status.HTTP_201_CREATED)
                else:
                    print(serializer.errors)
                    return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"입력 값 오류"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"이미 작성한 리뷰가 있습니다."}, status = status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"Body에 요소가 빠졌습니다."}, status = status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT': #리뷰 수정 API
        data = JSONParser().parse(request)
        reviewQuery = Review.objects.get(RID=pk)
        if reviewQuery is not None:
            if reviewQuery.UID.UID == flag:
                if data['contents'] is not None and data['rating'] is not None:
                    reviewQuery.contents = data['contents']
                    tempValue = float(reviewQuery.rating)
                    reviewQuery.rating = float(data['rating'])

                    bookQuery = TempBook.objects.get(TBID = int(reviewQuery.TBID.TBID))
                    reviewCnt = len(Review.objects.filter(TBID = bookQuery.TBID))
                    if reviewCnt == 1:
                        tempRating = float(data['rating'])
                    else:
                        tempRating = (float(bookQuery.RATING) * float(reviewCnt) - tempValue + float(data['rating'])) / float(reviewCnt)
                    bookQuery.RATING = tempRating
                    bookQuery.save()
                    reviewQuery.save()
                    temp = reviewQuery.like
                    isLike = False
                    if temp.count(flag) > 0:
                        isLike = True
                    returnDict = {
                        'RID':pk,
                        'TBID':reviewQuery.TBID.TBID,
                        'UID':reviewQuery.UID.UID,
                        'contents':reviewQuery.contents,
                        'views':reviewQuery.views,
                        'createAt':reviewQuery.createAt,
                        'likeCnt':len(reviewQuery.like),
                        'rating':reviewQuery.rating,
                        'isAccessible': True,
                        'isLiked' : isLike
                        }
                    return JsonResponse({'success':True, 'result':{'review':returnDict}, 'errorMessage':""}, status = status.HTTP_200_OK)
                else:
                    return JsonResponse({'success':False,'result':{'review':exceptDict},'errorMessage':"잘못된 형식의 Body입니다."},status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'success':False,'result':{'review':exceptDict},'errorMessage':"해당 RID의 리뷰는 존재하지 않습니다."},status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success':False,'result':{'review':exceptDict},'errorMessage':"권한이 없습니다."},status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'DELETE': #리뷰 삭제 API
        reviewQuery = Review.objects.get(RID=pk)
        if reviewQuery is not None:
            if reviewQuery.UID.UID == flag:
                bookQuery = TempBook.objects.get(TBID = int(reviewQuery.TBID.TBID))
                reviewCnt = len(Review.objects.filter(TBID = bookQuery.TBID))
                if reviewCnt -1 == 0:
                    reviewCnt = 2
                tempRating = (float(bookQuery.RATING) * float(reviewCnt) - float(reviewQuery.rating)) / (float(reviewCnt) - 1.0)
                bookQuery.RATING = tempRating
                bookQuery.save()
                reviewQuery.delete()
                return JsonResponse({'success':True, 'result':{'review':exceptDict}, 'errorMessage':""}, status = status.HTTP_200_OK)
            else:
                return JsonResponse({'success':False,'result':{'review':exceptDict},'errorMessage':"해당 RID의 리뷰는 존재하지 않습니다."},status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success':False,'result':{'review':exceptDict},'errorMessage':"권한이 없습니다."},status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(
    method='get',
    operation_description="리뷰를 가져올 책의 BID를 ID에 입력",
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
def bookReviews(request, pk): #책에 관한 리뷰를 받아오는 API
    flag = checkAuth_decodeToken(request)
    exceptDict = None
    if flag == 0:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    elif flag == -1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == -2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        reviewQuery = Review.objects.filter(TBID=pk)
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
                i['createAt'] = datetime.datetime.strptime(i["createAt"], '%Y-%m-%dT%H:%M:%S.%f').strftime("%Y-%m-%d %H:%M")
                i['userThumbnail'] = temp.thumbnail
                tempQuery = TempBook.objects.get(TBID = i['TBID'])
                i['AUTHOR'] = tempQuery.AUTHOR
                i['bookTitle'] = tempQuery.TITLE
                i['thumbnail'] = tempQuery.thumbnailImage
            return JsonResponse({'success':True, 'result':{'reviewList':serializers.data}, 'errorMessage':""}, status = status.HTTP_200_OK)
        else:
            return JsonResponse({'success':True, 'result':{'reviewList':exceptDict},'errorMessage':""},status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='put',
    operation_description="리뷰 좋아요 : 좋아요할 리뷰의 ID를 입력",
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "reviewLike": openapi.Schema('리뷰 좋아요 등록', type=openapi.TYPE_ARRAY, items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "isLiked": openapi.Schema('좋아요 했는지?', type=openapi.TYPE_BOOLEAN),
                               
                            })
                        )
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
@api_view(['PUT'])
def reviewLike(request, pk):
    flag = checkAuth_decodeToken(request)
    exceptDict = None
    if flag == 0:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    elif flag == -1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == -2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)
    returnDict = dict()
    if request.method == 'PUT':
        reviewQuery = Review.objects.get(RID = pk)
        if reviewQuery is not None:
            temp = reviewQuery.like
            cmpList = temp
            if cmpList.count(flag) > 0:
                temp.remove(flag)
                reviewQuery.like = temp
                reviewQuery.save()
                return JsonResponse({'success':True, 'result':{'isLiked':False},'errorMessage':""},status=status.HTTP_200_OK)
            else:
                reviewQuery.like = temp+[flag]
                reviewQuery.save()
                return JsonResponse({'success':True, 'result':{'isLiked':True},'errorMessage':""},status=status.HTTP_200_OK)        
        else:
            return JsonResponse({'success':False,'result':exceptDict,'errorMessage':"해당 RID의 리뷰가 없습니다"}, status = status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'success':False,'result':exceptDict,'errorMessage':"해당 RID의 리뷰가 없습니다"}, status = status.HTTP_405_Method_Not_Allowed)