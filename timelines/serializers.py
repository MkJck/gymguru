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
        # Automatically add the current user
        validated_data['user'] = self.context['request'].user
        timeline = Timeline.objects.create(**validated_data)
        return timeline


class KeyPhotoSerializer(serializers.ModelSerializer):
    """Serializer for KeyPhoto model"""
    
    # Fields for creation (from POST request)
    photo_taken_at = serializers.DateTimeField()
    weight_centigrams = serializers.IntegerField(required=False)  # Optional field
    
    class Meta:
        model = KeyPhoto
        fields = [
            'id', 'user', 'filename', 's3_path', 'presigned_url', 'uploaded_at', 'photo_taken_at',
            'weight_centigrams', 'file_size', 'created', 'updated', 'is_deleted'
        ]
        read_only_fields = [
            'id', 'user', 'uploaded_at', 'created', 'updated'
        ]
    
    def create(self, validated_data):
        """Create a new KeyPhoto object"""
        # Automatically add the current user
        validated_data['user'] = self.context['request'].user
        
        # If weight is not provided, generate a random one
        if 'weight_centigrams' not in validated_data:
            validated_data['weight_centigrams'] = KeyPhoto.generate_random_weight()
        
        # Other fields will be filled in the view
        return KeyPhoto.objects.create(**validated_data)