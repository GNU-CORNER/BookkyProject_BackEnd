from bookky.models import RecommendBook
from django.db.models import fields
from rest_framework import serializers

class RecommendPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendBook
        fields =['UID', 'BID'] 