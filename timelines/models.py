from django.db import models
from django.contrib.auth import get_user_model
from django.db import transaction
import random

User = get_user_model()

class Timeline(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timelines')
    name = models.CharField(max_length=100)
    # settings = models.JSONField()

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    class Meta:
        unique_together = ['user', 'name']


class TimelineType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class KeyPhoto(models.Model):
    """Model for storing key photos with weight data"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='key_photos', null=True, blank=True)
    filename = models.CharField(max_length=255)
    s3_path = models.CharField(max_length=500)
    presigned_url = models.URLField(max_length=500)  # Temporary file link
    uploaded_at = models.DateTimeField(auto_now_add=True)
    photo_taken_at = models.DateTimeField()
    weight_centigrams = models.IntegerField()
    file_size = models.BigIntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - KeyPhoto {self.filename} - {self.weight_centigrams/10}g - {self.photo_taken_at.date()}"
    
    @property
    def weight_grams(self):
        return self.weight_centigrams / 10
    
    @property
    def weight_kg(self):
        return self.weight_centigrams / 1000
    
    @classmethod
    def generate_random_weight(cls):
        return random.randint(700, 850)

    class Meta:
        unique_together = ['user', 'filename']


