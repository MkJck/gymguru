from django.urls import include, path
from . import views
from .views import TimelineTypeView, NewTimelineView

# URLconf
urlpatterns = [
    path('new/', NewTimelineView.as_view(), name='new-timeline'),
    path('types/', TimelineTypeView.as_view(), name='timeline-types'),
]