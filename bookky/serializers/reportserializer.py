from bookky.models import ReportingTable
from django.db.models import fields
from rest_framework import serializers

class ReportPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingTable
        fields = ['ReportId','UID','QPID','MPID','APID', 'reportType', 'TYPE']

class ReportCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingTable
        fields = ['ReportId','UID','QCID','MCID','ACID', 'reportType', 'TYPE']

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingTable
        fields = ['ReportId','UID','QCID','MCID','ACID', 'reportType','UID','QPID','MPID','APID','createAt', 'TYPE']
'''
class ReportingTable(models.Model):
    ReportId                = models.BigAutoField(primary_key=True)
    UID                     = models.ForeignKey("User", on_delete=models.CASCADE, null=False)
    #커뮤니티 글을 외래키로 두어서 좋을게 무엇이 있을까? // 관리자 테이블에서 삭제하기 위해서? -> communityType과 PID가 있지만 각각의 케이스를 코드로 써야함 -> 불필요 그냥 테이블에 컬럼을 추가하는게 추가적인 코드가 덜 필요하다.
    QPID                    = models.ForeignKey("QnACommunity", on_delete=models.CASCADE ,null=True)                        
    APID                    = models.ForeignKey("AnyCommunity", on_delete=models.CASCADE ,null=True)                        
    MPID                    = models.ForeignKey("MarketCommunity", on_delete=models.CASCADE ,null=True)                     #게시판 외래키
    createAt                = models.DateTimeField(auto_now_add=True, null=False)                                                   #생성날짜
    #커뮤니티 글을 자동 삭제는 쉽지만 엉뚱한 글 삭제가 일어날 수 있다. -> 즉, 수동으로 관리해야 한다. -> 관리자가 계속해서 검토해야 한다. -> 관리자 페이지를 작성해야 한다. 으악.
    reportContent           = models.TextField(verbose_name='신고 내용', null=False, blank=True)                          #null값을 줘야하나? 신고에는 무조건 사유가 필요하지 않나?

    def __str__(self):
        return self.ReportId 

{
    'reportType' : Integer, -> null : False
    'reportContent' : String -> null : False
}
Query = communityType=Integer&PID=Integer&CID=Integer&type=Integer
type = 0 이면 글
type = 1 이면 댓글
PID, CID는 해당 상황에 맞게 넣어주고 쿼리에서 빠져도 상관없음
단 두개중에 하나는 들어가 있어야 함
Header = access-token
'''
