from django.contrib import admin
from .models import TimelineType, Timeline, KeyPhoto


@admin.register(KeyPhoto)
class KeyPhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'filename', 'weight_grams', 'photo_taken_at', 'uploaded_at', 'is_deleted')
    list_filter = ('user', 'is_deleted', 'uploaded_at', 'photo_taken_at')
    search_fields = ('filename', 'user__username', 'user__email')
    readonly_fields = ('uploaded_at', 'created', 'updated')
    list_per_page = 50

@admin.register(TimelineType)
class TimelineTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'updated', 'created', 'is_deleted')
    list_filter = ('user', 'is_deleted', 'created', 'updated')
    search_fields = ('name', 'user__username', 'user__email')
    readonly_fields = ('created', 'updated')
    list_per_page = 50