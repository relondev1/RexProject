from django.contrib import admin
from .models import Model, ContentCreator, VideoProduction, VoiceArtist, ContentWriting, ContactMessage

@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'age', 'is_active', 'created_at')
    list_filter = ('gender', 'is_active', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('name', 'age', 'gender', 'height', 'experience')
        }),
        ('معلومات الاتصال', {
            'fields': ('email', 'phone')
        }),
        ('الوسائط', {
            'fields': ('image_url',)
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContentCreator)
class ContentCreatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'platform', 'is_active', 'created_at')
    list_filter = ('specialty', 'platform', 'is_active', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('name', 'specialty', 'platform', 'followers', 'experience')
        }),
        ('معلومات الاتصال', {
            'fields': ('email', 'phone')
        }),
        ('الوسائط', {
            'fields': ('image_url',)
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VideoProduction)
class VideoProductionAdmin(admin.ModelAdmin):
    list_display = ('name', 'video_type', 'quality', 'is_active', 'created_at')
    list_filter = ('video_type', 'quality', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('name', 'video_type', 'duration', 'quality', 'description')
        }),
        ('الوسائط', {
            'fields': ('video_url', 'thumbnail_url')
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VoiceArtist)
class VoiceArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'voice_type', 'specialty', 'is_active', 'created_at')
    list_filter = ('voice_type', 'is_active', 'created_at')
    search_fields = ('name', 'email', 'phone', 'specialty')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('name', 'voice_type', 'specialty', 'experience', 'languages')
        }),
        ('معلومات الاتصال', {
            'fields': ('email', 'phone')
        }),
        ('الوسائط', {
            'fields': ('audio_sample_url', 'image_url')
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContentWriting)
class ContentWritingAdmin(admin.ModelAdmin):
    list_display = ('name', 'writing_type', 'specialty', 'is_active', 'created_at')
    list_filter = ('writing_type', 'is_active', 'created_at')
    search_fields = ('name', 'email', 'phone', 'specialty')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('name', 'writing_type', 'specialty', 'experience', 'articles_count')
        }),
        ('معلومات الاتصال', {
            'fields': ('email', 'phone')
        }),
        ('الوسائط', {
            'fields': ('image_url',)
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'service', 'email', 'is_read', 'created_at')
    list_filter = ('service', 'is_read', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('name', 'email', 'phone', 'service')
        }),
        ('الرسالة', {
            'fields': ('message',)
        }),
        ('الحالة', {
            'fields': ('is_read',)
        }),
        ('التاريخ', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False