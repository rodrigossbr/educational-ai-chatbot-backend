from rest_framework import serializers


class SessionResponseSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
