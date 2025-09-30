from rest_framework import serializers

from ..models import Feedback


class FeedbackResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['user_message', 'chatbot_response', 'helpful', 'created_at']
