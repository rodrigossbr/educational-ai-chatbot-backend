from typing import Optional, Dict, Any

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import AskSerializer, BotMessageSerializer
from ..services import ChatbotService

_chatbotService = ChatbotService()

def generate_reply(user_text: str, session_id: Optional[int]) -> Dict[str, Any]:
    text = (user_text or "").strip()
    if not text:
        return {"reply": "Não entendi. Pode escrever novamente?", "detected_intent": "desconhecido"}

    try:
        result = _chatbotService.get_response(text, session_id=session_id)
        if isinstance(result, dict):
            return {
                "reply": result.get("answer", ""),
                "detected_intent": result.get("intent", "generativo"),
            }
        return {"reply": str(result), "detected_intent": "generativo"}
    except Exception:
        return {"reply": "Ops, tive um erro por aqui. Pode tentar de novo?", "detected_intent": "erro"}


@extend_schema(
    request=AskSerializer,
    responses={200: BotMessageSerializer},
    auth=None,
    summary="Endpoint para comunicação com o chatbot",
    description="Recebe uma mensagem e retorna uma resposta adaptada."
)
class AskController(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.data.get('session_id')
        user_text = serializer.validated_data.get('text')
        result = generate_reply(user_text, session_id)

        out_serializer = BotMessageSerializer(
            data={
                'id': 1,
                'role': 'bot',
                'text': result['reply'],
                'feedback_enabled': False if user_text == "Olá" else True,
                'detected_intent': result['detected_intent'],
            }
        )
        out_serializer.is_valid(raise_exception=True)
        return Response(out_serializer.data)
