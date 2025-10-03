from rest_framework import serializers


class AskSerializer(serializers.Serializer):
    text = serializers.CharField(
        max_length=500,
        help_text="A mensagem de texto do usuário para o chatbot."
    )
