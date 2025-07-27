from django.db import models
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Timeline(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    # settings = models.JSONField()

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TimelineType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


