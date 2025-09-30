from ..models import Feedback
from ..repositories import FeedbackRepository

class FeedbackService:
    def __init__(self):
        self.repository = FeedbackRepository()

    def submit_feedback(self, user_message, chatbot_response, helpful):
        feedback = Feedback(
            user_message=user_message,
            chatbot_response=chatbot_response,
            helpful=helpful
        )
        return self.repository.save(feedback)

    def get_all_feedback(self):
        return self.repository.get_all()