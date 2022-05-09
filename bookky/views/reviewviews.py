from bookky.models import Review, Book, User
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
                        "RID": openapi.Schema('리뷰아이디', type=openapi.TYPE_INTEGER),
                        "BID": openapi.Schema('책아이디', type=openapi.TYPE_INTEGER),
                        "UID": openapi.Schema('사용자아이디', type=openapi.TYPE_INTEGER),
                        "contents": openapi.Schema('리뷰내용', type=openapi.TYPE_STRING),
                        "views": openapi.Schema('리뷰조회수', type=openapi.TYPE_INTEGER),
                        "createAt": openapi.Schema('리뷰생성날짜', type=openapi.TYPE_STRING),
                        "likeCnt": openapi.Schema('리뷰 좋아요 개수', type=openapi.TYPE_INTEGER),
                        "rating": openapi.Schema('리뷰 평점', type=openapi.TYPE_INTEGER),
                        "isAccessible": openapi.Schema('리뷰 접근 권한 "True"이면 수정권한이 있고 "False"이면 없음', type=openapi.TYPE_BOOLEAN),
                        "isLiked" : openapi.Schema('좋아요 여부', type=openapi.TYPE_BOOLEAN),
                        "nickname": openapi.Schema('리뷰 작성자', type=openapi.TYPE_STRING),
                        "userthumbnail" : openapi.Schema('사용자 썸네일', type=openapi.TYPE_STRING)
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
                        'userData':openapi.Schema(
                            type = openapi.TYPE_OBJECT,
                            properties={
                                "RID": openapi.Schema('리뷰아이디', type=openapi.TYPE_INTEGER),
                                "BID": openapi.Schema('책아이디', type=openapi.TYPE_INTEGER),
                                "UID": openapi.Schema('사용자아이디', type=openapi.TYPE_INTEGER),
                                "contents": openapi.Schema('리뷰내용', type=openapi.TYPE_STRING),
                                "views": openapi.Schema('리뷰조회수', type=openapi.TYPE_INTEGER),
                                "createAt": openapi.Schema('리뷰생성날짜', type=openapi.TYPE_STRING),
                                "likeCnt": openapi.Schema('리뷰 좋아요 개수', type=openapi.TYPE_INTEGER),
                                "rating": openapi.Schema('리뷰 평점', type=openapi.TYPE_INTEGER),
                                "isAccessible": openapi.Schema('리뷰 접근 권한 "True"이면 수정권한이 있고 "False"이면 없음', type=openapi.TYPE_BOOLEAN),
                                "isLiked" : openapi.Schema('좋아요 여부', type=openapi.TYPE_BOOLEAN),
                                "nickname": openapi.Schema('리뷰 작성자', type=openapi.TYPE_STRING),
                                "userthumbnail" : openapi.Schema('사용자 썸네일', type=openapi.TYPE_STRING)
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
    elif flag == 1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == 2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_403_FORBIDDEN)

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
                temp = User.objects.get(UID=i['UID'])
                i['nickname'] = temp.nickname
                i['userthumbnail'] = temp.thumbnail
            reviewData = serializers.data
            reviewQuery = Review.objects.get(RID=pk)
            reviewQuery.views = reviewQuery.views + 1
            reviewData[0]['views'] = reviewQuery.views
            reviewQuery.save()
            return JsonResponse({'success':True, 'result':{'reviewList':reviewData[0]}, 'errorMessage':""}, status = status.HTTP_200_OK)
        else:
            return JsonResponse({'success':True, 'result':{'reviewList':exceptDict},'errorMessage':"해당 아이디의 리뷰가 존재하지 않습니다."},status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'POST': #리뷰 등록 API
        data = JSONParser().parse(request)
        if data['contents'] is not None:
            data['UID'] = flag
            data['BID'] = pk
            temp = Review.objects.filter(                    
                Q(BID = pk) & #책 소개
                Q(UID = flag)
            )
            print(len(temp))
            if len(temp) == 0: 
                serializer = ReviewPostSerializer(data = data)
                if serializer.is_valid():
                    bookQuery = Book.objects.get(BID = pk)
                    reviewCnt = len(Review.objects.filter(BID = pk))
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
                    tempData['userthumbnail'] = temp.thumbnail
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

                    bookQuery = Book.objects.get(BID = int(reviewQuery.BID.BID))
                    reviewCnt = len(Review.objects.filter(BID = bookQuery.BID))
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
                        'BID':reviewQuery.BID.BID,
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
                bookQuery = Book.objects.get(BID = int(reviewQuery.BID.BID))
                reviewCnt = len(Review.objects.filter(BID = bookQuery.BID))
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
                                "RID": openapi.Schema('리뷰아이디', type=openapi.TYPE_INTEGER),
                                "BID": openapi.Schema('책아이디', type=openapi.TYPE_INTEGER),
                                "UID": openapi.Schema('사용자아이디', type=openapi.TYPE_INTEGER),
                                "contents": openapi.Schema('리뷰내용', type=openapi.TYPE_STRING),
                                "views": openapi.Schema('리뷰조회수', type=openapi.TYPE_INTEGER),
                                "createAt": openapi.Schema('리뷰생성날짜', type=openapi.TYPE_STRING),
                                "likeCnt": openapi.Schema('리뷰 좋아요 개수', type=openapi.TYPE_INTEGER),
                                "rating": openapi.Schema('리뷰 평점', type=openapi.TYPE_INTEGER),
                                "isAccessible": openapi.Schema('리뷰 접근 권한 "True"이면 수정권한이 있고 "False"이면 없음', type=openapi.TYPE_BOOLEAN),
                                "isLiked" : openapi.Schema('좋아요 여부', type=openapi.TYPE_BOOLEAN),
                                "nickname": openapi.Schema('리뷰 작성자', type=openapi.TYPE_STRING),
                                "userthumbnail" : openapi.Schema('사용자 썸네일', type=openapi.TYPE_STRING)
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
    elif flag == 1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == 2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        reviewQuery = Review.objects.filter(BID=pk)
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
                i['userthumbnail'] = temp.thumbnail
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
                                "RID": openapi.Schema('리뷰아이디', type=openapi.TYPE_INTEGER),
                                "UID": openapi.Schema('사용자아이디', type=openapi.TYPE_INTEGER)
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
    operation_description="리뷰 좋아요 삭제: 좋아요할 리뷰의 ID를 입력",
    manual_parameters=[openapi.Parameter('access-token', openapi.IN_HEADER, description="접근 토큰", type=openapi.TYPE_STRING)],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema('호출 성공여부', type=openapi.TYPE_BOOLEAN),
                'result': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "reviewLike": openapi.Schema('리뷰 좋아요 삭제', type=openapi.TYPE_ARRAY, items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={

                            })
                        )
                    }
                ),
                'errorMessage': openapi.Schema('에러 메시지', type=openapi.TYPE_STRING)
            }
        )
    }
)
@api_view(['PUT','DELETE'])
def reviewLike(request, pk):
    flag = checkAuth_decodeToken(request)
    exceptDict = None
    if flag == 0:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    elif flag == 1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == 2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_403_FORBIDDEN)
    returnDict = dict()
    if request.method == 'PUT':
        reviewQuery = Review.objects.get(RID = pk)
        if reviewQuery is not None:
            temp = reviewQuery.like
            reviewQuery.like = temp+[flag]
            reviewQuery.save()
            returnDict = {'RID' : pk, 'UID' : flag}
            return JsonResponse({'success':True, 'result':{'reviewLike':returnDict},'errorMessage':""},status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False,'result':exceptDict,'errorMessage':"해당 RID의 리뷰가 없습니다"}, status = status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        reviewQuery = Review.objects.get(RID = pk)
        if reviewQuery is not None:
            temp = reviewQuery.like
            temp.remove(flag)
            reviewQuery.like = temp
            reviewQuery.save()
            return JsonResponse({'success':True, 'result':{'reviewLike':None},'errorMessage':""},status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success':False,'result':exceptDict,'errorMessage':"해당 RID의 리뷰가 없습니다"}, status = status.HTTP_400_BAD_REQUEST)
    
    else:
        return JsonResponse({'success':False,'result':exceptDict,'errorMessage':"해당 호출방식은 지원하지 않습니다."}, status = status.HTTP_405_METHOD_NOT_ALLOWED)