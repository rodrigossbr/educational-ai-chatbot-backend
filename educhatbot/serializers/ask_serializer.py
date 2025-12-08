from rest_framework import serializers

class HistoryItemSerializer(serializers.Serializer):
    role = serializers.CharField(help_text="Quem enviou: 'user' ou 'bot'")
    text = serializers.CharField(help_text="O conteúdo da mensagem")

class AskSerializer(serializers.Serializer):
    session_id = serializers.IntegerField(help_text="Id da sessão do chatboot")
    role = serializers.CharField(help_text="Quem enviou a mensagem: 'user' ou 'bot'")
    text = serializers.CharField(max_length=500, help_text="A mensagem de texto do usuário para o chatbot.")
    simplify = serializers.BooleanField(required=False, default=False, help_text="Indica se o texto deve ser simplificado no chatbot.")
    last_messages = HistoryItemSerializer(
        many=True,
        required=False,
        default=[],
        help_text="Histórico recente da conversa para contexto do NLU"
    )