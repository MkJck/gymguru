from django.urls import include, path
from . import views
from .views import TimelineTypeView, NewTimelineView, PhotoUploadView, KeyPhotoUploadView, KeyPhotoDetailView, KeyPhotoDownloadView, UserKeyPhotosView, UserTimelinesView

# URLconf
urlpatterns = [
    path('new-timeline/', NewTimelineView.as_view(), name='new-timeline'),
    path('timeline-types/', TimelineTypeView.as_view(), name='timeline-types'),
    path('upload-on-server/', PhotoUploadView.as_view(), name='upload-on-server'),
    path('keyphoto/new/', KeyPhotoUploadView.as_view(), name='keyphoto-upload'),
    path('keyphoto/<int:pk>/', KeyPhotoDetailView.as_view(), name='keyphoto-detail'),
    path('keyphoto/<int:pk>/download/', KeyPhotoDownloadView.as_view(), name='keyphoto-download'),
    path('my-keyphotos/', UserKeyPhotosView.as_view(), name='user-keyphotos'),
    path('my-timelines/', UserTimelinesView.as_view(), name='user-timelines'),
]