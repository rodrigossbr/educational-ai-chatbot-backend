from operator import truediv

from rest_framework import serializers


class FeedbackRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    session_id = serializers.IntegerField(required=False, allow_null=True)
    user_question = serializers.CharField(max_length=500, help_text="Mensagem enviada pelo usuário.")
    bot_answer = serializers.CharField(max_length=500, help_text="Mensagem enviada pelo chatboot.")
    helpful = serializers.BooleanField(required=False, allow_null=True, help_text="Indica se a resposta do chatbot foi útil.")


