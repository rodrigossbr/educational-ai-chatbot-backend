from django.db.models import Max

from ..models import Feedback


class FeedbackRepository:

    @staticmethod
    def get_next_session_id() -> int:
        last = (
            Feedback.objects
            .filter(session_id__isnull=False)
            .aggregate(m=Max("session_id"))
            .get("m")
        )
        return (last or 0) + 1

    @staticmethod
    def get_by_id(feedback_id):
        return Feedback.objects.get(pk=feedback_id)

    @staticmethod
    def save(model: Feedback):
        return model.save()

    @staticmethod
    def get_all():
        return Feedback.objects.all()

    @staticmethod
    def mark_consumed(feedback: Feedback):
        feedback.consumed = True
        feedback.save(update_fields=["consumed"])

    @staticmethod
    def get_last_unconsumed_negative(session_id: int | None):
        if not session_id:
            return None
        return (
            Feedback.objects
            .filter(session_id=session_id, helpful=False, consumed=False)
            .order_by("-created_at")
            .first()
        )
