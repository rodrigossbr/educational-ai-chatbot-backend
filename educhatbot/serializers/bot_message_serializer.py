from rest_framework import serializers


class BotMessageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    role = serializers.CharField(
        read_only=True,
        default="bot",
        help_text="Tipo de resposta do chatbot."
    )
    text = serializers.CharField(
        help_text="A resposta do chatbot."
    )
