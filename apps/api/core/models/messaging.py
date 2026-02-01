from __future__ import annotations

from django.conf import settings
from django.db import models

from .base import TimestampedModel


class Conversation(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    episode = models.ForeignKey(
        "Episode", on_delete=models.SET_NULL, null=True, blank=True
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="conversations"
    )

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.id}"


class Message(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    body = models.TextField()

    class Meta:
        ordering = ("created_at", "id")

    def __str__(self) -> str:
        return f"{self.conversation_id}:{self.id}"


class MessageRead(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="reads")
    reader = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="message_reads"
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("message", "reader")

    def __str__(self) -> str:
        return f"{self.message_id}:{self.reader_id}"
