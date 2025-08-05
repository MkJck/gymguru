from django.urls import include, path
from . import views
from .views import TimelineTypeView, NewTimelineView, PhotoUploadView, KeyPhotoUploadView, KeyPhotoDetailView, KeyPhotoDownloadView

# URLconf
urlpatterns = [
    path('new-timeline/', NewTimelineView.as_view(), name='new-timeline'),
    path('timeline-types/', TimelineTypeView.as_view(), name='timeline-types'),
    path('upload-on-server/', PhotoUploadView.as_view(), name='upload-on-server'),
    path('keyphoto/new/', KeyPhotoUploadView.as_view(), name='keyphoto-upload'),
    path('keyphoto/<int:pk>/', KeyPhotoDetailView.as_view(), name='keyphoto-detail'),
    path('keyphoto/<int:pk>/download/', KeyPhotoDownloadView.as_view(), name='keyphoto-download'),
]