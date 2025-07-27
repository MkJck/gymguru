from django.shortcuts import render
from django.http import JsonResponse

from rest_framework import permissions, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from timelines.serializers import TimelineTypeSerializer, NewTimelineSerializer
from timelines.models import TimelineType
    
class TimelineTypeView(generics.ListAPIView):

    queryset = TimelineType.objects.all()
    serializer_class = TimelineTypeSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get']


class NewTimelineView(APIView):
    permission_classes = [permissions.AllowAny]

    # @csrf_exempt
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

    def post(self, request):
        serializer = NewTimelineSerializer(
            data=request.data,
            context={'request': request}
            )
        if serializer.is_valid():
            timeline = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)