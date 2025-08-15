from django.db import models
from django.conf import settings

# Create your models here

class AILogs(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    prompt = models.TextField()
    response = models.TextField()

    model_name = models.CharField(max_length=100, blank=True)
    duration_ms = models.PositiveIntegerField(help_text="Duration in milliseconds", null=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AILog for {self.user} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"