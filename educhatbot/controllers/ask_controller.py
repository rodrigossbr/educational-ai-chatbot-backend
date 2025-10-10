from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import AskSerializer, BotMessageSerializer
from ..services import ChatbotService


def generate_reply(user_text: str) -> str:
    cleaned_text = user_text.strip()
    chatbotService = ChatbotService()
    if not cleaned_text:
        return "Não entendi. Pode escrever novamente?"
    resul_text = chatbotService.get_response(cleaned_text)
    return f"{resul_text}"


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

        user_text = serializer.validated_data.get('text')
        bot_text = generate_reply(user_text)

        out_serializer = BotMessageSerializer(
            data={
                'id': 1,
                'role': 'bot',
                'text': bot_text
            }
        )
        out_serializer.is_valid(raise_exception=True)
        return Response(out_serializer.data)
