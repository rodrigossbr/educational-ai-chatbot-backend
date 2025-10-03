from django.urls import path

from .controllers import AskController, FeedbackController

urlpatterns = [
    path('chat', AskController.as_view(), name='chat-api'),
    path('feedback', FeedbackController.as_view(), name='feedback-api'),
]
