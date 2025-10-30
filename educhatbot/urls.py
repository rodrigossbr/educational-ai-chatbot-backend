from django.urls import path

from .controllers import AskController, FeedbackController
from .controllers.session_controller import SessionController

urlpatterns = [
    path('chat', AskController.as_view(), name='chat-api'),
    path('feedback', FeedbackController.as_view(), name='feedback-api'),
    path('session', SessionController.as_view(), name='session-api'),
]
