from django.contrib.auth.models import User
from django.db import models


class Friendship(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friendship')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friendship')
    sent_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    pending = models.BooleanField(default=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f'{self.sender.username} -> {self.receiver.username}'
