from rest_framework import serializers

from ..models import Feedback


class FeedbackResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    session_id = serializers.IntegerField(required=False, allow_null=True)
    user_question = serializers.CharField()
    bot_answer = serializers.CharField()
    helpful = serializers.BooleanField()
    created_at = serializers.DateTimeField()

    def to_representation(self, instance: Feedback):
        return {
            "id": instance.id,
            "session_id": instance.session_id,
            "user_question": instance.user_question,
            "bot_answer": instance.bot_answer,
            "helpful": instance.helpful,
            "created_at": instance.created_at,
        }
