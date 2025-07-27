from rest_framework import serializers
from .models import TimelineType, Timeline

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