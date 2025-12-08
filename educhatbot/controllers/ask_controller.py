from typing import Optional, Dict, Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import AskSerializer, BotMessageSerializer
from ..services import ChatbotService


@extend_schema(
    request=AskSerializer,
    responses={200: BotMessageSerializer},
    auth=None,
    summary="Endpoint para comunicação com o chatbot",
    description="Recebe uma mensagem e retorna uma resposta adaptada."
)
class AskController(APIView):
    permission_classes = [AllowAny]

    def __init__(self):
        self.chatbot_service = ChatbotService()

    def post(self, request):
        serializer = AskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.data.get('session_id')
        user_text = serializer.validated_data.get('text')
        simplify = serializer.validated_data.get('simplify', False)
        last_messages = serializer.validated_data.get('last_messages', [])

        if not user_text:
            return self._build_response("Não entendi. Pode escrever novamente?", "desconhecido")

        try:
            result = self.chatbot_service.get_response(
                user_input=user_text,
                session_id=session_id,
                simplify=simplify,
                last_messages=last_messages
            )

            reply_text = result.get("answer", "") if isinstance(result, dict) else str(result)
            intent = result.get("intent", "generativo") if isinstance(result, dict) else "generativo"

            return self._build_response(reply_text, intent, feedback_enabled=(user_text != "Olá"))

        except Exception as e:
            print(f"Erro no controller: {e}")
            return self._build_response("Ops, tive um erro por aqui. Pode tentar de novo?", "erro")

    @staticmethod
    def _build_response(text: str, intent: str, feedback_enabled: bool = True):
        """Método auxiliar privado apenas para formatar o JSON de saída"""
        out_serializer = BotMessageSerializer(
            data={
                'id': 1,
                'role': 'bot',
                'text': text,
                'feedback_enabled': feedback_enabled,
                'detected_intent': intent,
            }
        )
        out_serializer.is_valid(raise_exception=True)
        return Response(out_serializer.data, status=status.HTTP_200_OK)