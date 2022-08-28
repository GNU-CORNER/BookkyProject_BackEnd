from bookky.auth.auth import checkAuth_decodeToken
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from django.db.models import Q
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg import openapi

from bookky.models import ReportingTable, SuperUser
from bookky.serializers.reportserializer import ReportPostSerializer, ReportCommentSerializer, ReportSerializer
'''
신고기능과 함께 들어갈 기능
1. 글 신고기능 v
2. 댓글 신고기능 v
3. 어드민 페이지에 신고 내역을 뿌려줄 기능 v (권한 테이블 추가)
4. 어드민 페이지에서 삭제, 반려 기능
5. 유저 제제 기능 (이거 좀 히튼데.. 어케하지 -> 회의 필요)
6. 어드민 페이지 작성
'''

@api_view(['POST'])
def userReport(request): #커뮤니티 글 신고 등록 기능  DB에 올라오게끔 해야함
    flag = checkAuth_decodeToken(request) #AT 체크
    exceptDict = None
    if flag == 0:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    elif flag == -1:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    elif flag == -2:
        return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        parseData = JSONParser().parse(request)
        parseData['UID'] = flag
        communityType = int(request.GET.get('communityType'))

        if int(parseData['TYPE']) == 0 : 

            PID = int(request.GET.get('PID'))
            if parseData['reportType'] is not None:
                if communityType == 0 :
                    parseData['APID'] = PID
                    reportSerializer = ReportPostSerializer(data=parseData)

                elif communityType == 1 :
                    parseData['MPID'] = PID
                    reportSerializer = ReportPostSerializer(data=parseData)

                elif communityType == 2 :
                    parseData['QPID'] = PID
                    reportSerializer = ReportPostSerializer(data=parseData)

                    if reportSerializer.is_valid():
                        reportSerializer.save()
                        return JsonResponse({'success':True, 'result':reportSerializer.data,'errorMessage':""}, status=status.HTTP_201_CREATED)
                    else:
                        return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"Body값을 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"communityType을 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"reportType을 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)
            
        elif int(parseData['TYPE']) == 1 :

            CID = int(request.GET.get('CID'))
            if parseData['reportType'] is not None:
                if communityType == 0 :
                    parseData['ACID'] = CID
                    reportSerializer = ReportCommentSerializer(data=parseData)

                elif communityType == 1 :
                    parseData['MCID'] = CID
                    reportSerializer = ReportCommentSerializer(data=parseData)

                elif communityType == 2 :
                    parseData['QCID'] = CID
                    reportSerializer = ReportCommentSerializer(data=parseData)

                    if reportSerializer.is_valid():
                        reportSerializer.save()
                        return JsonResponse({'success':True, 'result':reportSerializer.data,'errorMessage':""}, status=status.HTTP_201_CREATED)
                    else:
                        return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"Body값을 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"communityType을 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"reportType을 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success':False, 'result':exceptDict,'errorMessage':"type을 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def printReport(request):
    # flag = checkAuth_decodeToken(request) #AT 체크
    # exceptDict = None
    # if flag == 0:
    #     return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 없습니다."}, status = status.HTTP_400_BAD_REQUEST)
    # elif flag == -1:
    #     return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"잘못된 AT입니다."}, status = status.HTTP_403_FORBIDDEN)
    # elif flag == -2:
    #     return JsonResponse({'success':False, 'result':exceptDict, 'errorMessage':"AT가 만료되었습니다."}, status = status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET':
        # if checkAuthority(flag):
            print("Admin access")
            reportObject = ReportingTable.objects.all()
            dataObject = dict()
            serializer = ReportSerializer(reportObject, many=True)
            return JsonResponse({'success':True, 'data':serializer.data, 'errorMessage':""},status = status.HTTP_200_OK)
        # else:
        #     return JsonResponse({'success':False,'data':exceptDict,'errorMessage':"허용되지 않은 접근"}, status = status.HTTP_403_FORBIDDEN)

def checkAuthority(UID):
    query = SuperUser.objects.get(UID=UID)
    if int(query.authority) == 1 or int(query.authority) == 2:
        return True
    else:
        return False