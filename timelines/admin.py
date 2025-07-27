from django.contrib import admin
from .models import TimelineType, Timeline

@admin.register(TimelineType)
class TimelineTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'updated', 'created', 'is_deleted')

# @admin.register(KeyPhoto)
# class KeyPhotoAdmin(admin.ModelAdmin):
#     list_display = ('timeline', 'date_taken', 'weight')

# @admin.register(Transition)
# class TransitionAdmin(admin.ModelAdmin):
#     list_display = ('timeline', 'created_at', 'is_ready')