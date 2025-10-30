from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import SessionResponseSerializer
from ..services import FeedbackService


@extend_schema(
    auth=None,
    summary="Sessão do usuário",
    description="Busca informações da sessão do usuário"
)
class SessionController(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FeedbackService()

    @extend_schema(
        responses={200: SessionResponseSerializer(many=True)},
        summary="Busca a próxima sessão",
        description="Retorna o id da sessão."
    )
    def get(self, request):
        next_id = self.service.get_next_session_id()
        serializer = SessionResponseSerializer({"session_id": next_id})
        return Response(serializer.data)
