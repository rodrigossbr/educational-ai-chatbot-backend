from rest_framework import serializers


class AskSerializer(serializers.Serializer):
    session_id = serializers.IntegerField(help_text="Id da sessão do chatboot")
    text = serializers.CharField(max_length=500, help_text="A mensagem de texto do usuário para o chatbot.")
    simplify = serializers.BooleanField(required=False, default=False, help_text="Indica se o texto deve ser simplificado no chatbot.")
