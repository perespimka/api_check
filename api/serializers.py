from rest_framework import serializers
from .models import UserRequest

class UserRequestSerializer(serializers.ModelSerializer):
    class Meta():
        model = UserRequest
        fields = ('request_type', 'link', 'request_mime', 'request_text', 'request_headers')