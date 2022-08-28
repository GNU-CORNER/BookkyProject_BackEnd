from django.db.models import fields
from rest_framework import serializers

from bookky.models import SuperUser

class AuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperUser
        fields = ['UID','authority']
