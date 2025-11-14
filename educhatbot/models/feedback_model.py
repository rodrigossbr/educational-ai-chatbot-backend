from operator import truediv

from django.db import models


class Feedback(models.Model):
    id = models.BigAutoField(primary_key=True)
    session_id = models.BigIntegerField(null=True, blank=True, help_text="ID da sessão no momento do feedback (opcional).")
    user_question = models.TextField(default='', blank=True, max_length=8000, help_text="Pergunta do usuário no momento do feedback.")
    bot_answer = models.TextField(default='', blank=True, max_length=8000, help_text="Resposta do bot que foi avaliada.")
    helpful = models.BooleanField(blank=True, null=True, help_text="True = ajudou (like), False = não ajudou (dislike).")
    consumed = models.BooleanField(default=False, help_text="Se o backend já usou este feedback para adaptar a resposta.")
    detected_intent = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        help_text="Intent que o NLU detectou quando essa resposta foi gerada."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback em {self.created_at.strftime("%Y-%m-%d %H:%M:%S")} {'T' if self.helpful else 'F'}] {self.bot_answer[:40]}'
