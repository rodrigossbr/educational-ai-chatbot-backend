from django.urls import path

from .controllers import ChatbotController, FeedbackController

urlpatterns = [
    path('chat/', ChatbotController.as_view(), name='chat-api'),
    path('feedback/', FeedbackController.as_view(), name='feedback-api'),
]
