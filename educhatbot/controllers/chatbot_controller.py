from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from ..serializers import ChatbotRequestSerializer, ChatbotResponseSerializer

@extend_schema(
    request=ChatbotRequestSerializer,
    responses={200: ChatbotResponseSerializer},
    auth=None,
    summary="Endpoint para comunicação com o chatbot",
    description="Recebe uma mensagem e retorna uma resposta adaptada."
)
class ChatbotController(APIView):
    def post(self, request):
        serializer = ChatbotRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = serializer.validated_data.get('message')

        # ... sua lógica de chatbot ...

        response_data = {
            'text_response': f"Resposta para: {user_message}",
            'audio_url': 'url_de_teste',
            'libras_url': 'url_de_teste'
        }
        return Response(response_data)