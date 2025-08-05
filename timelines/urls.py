from django.urls import include, path
from . import views
from .views import TimelineTypeView, NewTimelineView, PhotoUploadView, PhotoListView, PhotoDetailView, test_upload_page, test_keyphoto_upload_page, KeyPhotoUploadView

# URLconf
urlpatterns = [
    path('new/', NewTimelineView.as_view(), name='new-timeline'),
    path('types/', TimelineTypeView.as_view(), name='timeline-types'),
    path('upload-photo/', PhotoUploadView.as_view(), name='upload-photo'),
    path('photos/', PhotoListView.as_view(), name='photo-list'),
    path('photos/<str:filename>/', PhotoDetailView.as_view(), name='photo-detail'),
    path('test-upload/', test_upload_page, name='test-upload'),
    path('test-keyphoto-upload/', test_keyphoto_upload_page, name='test-keyphoto-upload'),
    path('keyphoto/new/', KeyPhotoUploadView.as_view(), name='keyphoto-upload'),
]