from ..models import Feedback

class FeedbackRepository:
    @staticmethod
    def save(model: Feedback):
        return model.save()

    @staticmethod
    def get_all():
        return Feedback.objects.all()