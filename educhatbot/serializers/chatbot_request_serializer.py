from rest_framework import serializers


class ChatbotRequestSerializer(serializers.Serializer):
    message = serializers.CharField(
        max_length=500,
        help_text="A mensagem de texto do usuário para o chatbot."
    )
