from rest_framework import serializers


class FeedbackRequestSerializer(serializers.Serializer):
    user_message = serializers.CharField(max_length=500, help_text="Mensagem enviada pelo usuário.")
    chatbot_response = serializers.CharField(max_length=500, help_text="Mensagem enviada pelo chatboot.")
    helpful = serializers.BooleanField(help_text="Indica se a resposta do chatbot foi útil.")