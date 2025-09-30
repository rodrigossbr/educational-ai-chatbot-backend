from rest_framework import serializers


class ChatbotResponseSerializer(serializers.Serializer):
    response = serializers.CharField(
        help_text="A resposta do chatbot."
    )
