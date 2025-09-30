from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models.feedback_model import Feedback

admin.site.register(Feedback)

