from rest_framework import serializers
from .models import TimelineType, Timeline, KeyPhoto
from datetime import datetime

class TimelineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineType
        fields = ['id', 'name']


class NewTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = ['name']

    def create(self, validated_data):
        timeline = Timeline.objects.create(**validated_data)
        return timeline


class KeyPhotoSerializer(serializers.ModelSerializer):
    """Сериализатор для модели KeyPhoto"""
    
    # Поля для создания (из POST запроса)
    photo_taken_at = serializers.DateTimeField()
    weight_centigrams = serializers.IntegerField(required=False)  # Опциональное поле
    
    class Meta:
        model = KeyPhoto
        fields = [
            'id', 'filename', 's3_path', 's3_url', 
            'uploaded_at', 'photo_taken_at', 'weight_centigrams',
            'file_size', 'content_type', 'created', 'updated'
        ]
        read_only_fields = [
            'id', 'filename', 's3_path', 's3_url', 
            'uploaded_at', 'file_size', 'content_type', 'created', 'updated'
        ]
    
    def create(self, validated_data):
        """Создает новый объект KeyPhoto"""
        # Если вес не передан, генерируем случайный
        if 'weight_centigrams' not in validated_data:
            validated_data['weight_centigrams'] = KeyPhoto.generate_random_weight()
        
        # Остальные поля будут заполнены в view
        return KeyPhoto.objects.create(**validated_data)