
from django.db import models

class Feedback(models.Model):
    user_message = models.TextField()
    chatbot_response = models.TextField()
    helpful = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback em {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'