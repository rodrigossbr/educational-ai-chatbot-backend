from difflib import SequenceMatcher
from typing import Optional

from ..models import Feedback
from ..repositories import FeedbackRepository


class FeedbackService:
    def __init__(self):
        self.repository = FeedbackRepository()

    def get_next_session_id(self) -> int:
        return self.repository.get_next_session_id()

    def submit_feedback(
            self, feedback_id, session_id,
            user_message, chatbot_response, helpful, detected_intent
    ):
        if feedback_id:
            feedback = self.repository.get_by_id(feedback_id)
            if session_id is not None:
                feedback.session_id = session_id
            if user_message is not None:
                feedback.user_question = user_message
            if chatbot_response is not None:
                feedback.bot_answer = chatbot_response

            if helpful is not None:
                feedback.helpful = helpful
        else:
            feedback = Feedback(
                session_id=session_id,
                user_question=user_message,
                bot_answer=chatbot_response,
                helpful=helpful,
                detected_intent=detected_intent
            )
        self.repository.save(feedback)
        return feedback

    def get_all_feedback(self):
        return self.repository.get_all()

    def mark_consumed(self, feedback: Feedback):
        return self.repository.mark_consumed(feedback)

    def get_last_unconsumed_negative(self, session_id: int | None):
        return self.repository.get_last_unconsumed_negative(session_id)

    def get_last_feedback(self, session_id: int) -> Optional[Feedback]:
        if not session_id:
            return None
        return (
            Feedback.objects
            .filter(session_id=session_id)
            .order_by("-created_at")
            .first()
        )

    def session_needs_simplify(self, session_id: int) -> bool:
        """
        True se o último feedback da sessão foi 'não ajudou'.
        """
        last = self.get_last_feedback(session_id)
        return bool(last and last.helpful is False)

    def find_similar_negative_feedbacks(
            self,
            user_message: str,
            min_score: float = 0.65,
            limit: int = 3,
    ) -> list[Feedback]:
        """
        Procura feedbacks anteriores (de todo mundo) que deram 'não ajudou'
        e que são parecidos com a pergunta atual.
        Usa difflib só pra ter algo simples.
        """
        if not user_message:
            return []

        candidates = Feedback.objects.filter(helpful=False).order_by("-created_at")[:200]

        user_msg_norm = user_message.lower()
        scored: list[tuple[float, Feedback]] = []

        for fb in candidates:
            fb_msg = (fb.user_question or "").lower()
            score = SequenceMatcher(None, user_msg_norm, fb_msg).ratio()
            if score >= min_score:
                scored.append((score, fb))

        scored.sort(key=lambda t: t[0], reverse=True)
        return [fb for score, fb in scored[:limit]]

    def get_negative_intents_for_similar_text(self, text: str, min_score: float = 0.7):
        """
        Retorna uma lista de intents que já foram rejeitadas (helpful=False)
        para perguntas parecidas com o texto atual.
        """
        if not text:
            return []

        bads = (
            Feedback.objects
            .filter(helpful=False)
            .exclude(detected_intent__isnull=True)
            .exclude(detected_intent__exact="")
            .order_by("-created_at")[:200]
        )

        text_norm = text.lower()
        intents = set()
        for fb in bads:
            prev = (fb.user_question or "").lower()
            score = SequenceMatcher(None, text_norm, prev).ratio()
            if score >= min_score:
                intents.add(fb.detected_intent)

        return list(intents)