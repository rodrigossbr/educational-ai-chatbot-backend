from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import FeedbackRequestSerializer, FeedbackResponseSerializer
from ..services import FeedbackService


@extend_schema(
    auth=None,
    summary="Feedbacks do usuário",
    description="Gerencias os feedbacks do usuário"
)
class FeedbackController(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FeedbackService()

    @extend_schema(
        request=FeedbackRequestSerializer,
        responses={200: FeedbackResponseSerializer},
        auth=None,
        summary="Registrar feedback do usuário",
        description="Registra se a resposta do chatbot foi útil."
    )
    def post(self, request):
        serializer = FeedbackRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        saved_feedback = self.service.submit_feedback(
            data.get("id", None),
            data.get("session_id"),
            data.get("user_question"),
            data.get("bot_answer"),
            data.get("helpful", None),
            data.get("detected_intent", None)
        )

        serializer = FeedbackResponseSerializer(saved_feedback)
        return Response(serializer.data)

    @extend_schema(
        responses={200: FeedbackResponseSerializer(many=True)},
        summary="Listar todos os feedbacks",
        description="Retorna uma lista de todos os feedbacks registrados no sistema."
    )
    def get(self, request):
        feedbacks = self.service.get_all_feedback()
        serializer = FeedbackResponseSerializer(feedbacks, many=True)
        return Response(serializer.data)
