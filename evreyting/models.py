from django.db import models
from django.contrib.auth.models import User
# =========================
# Model
# =========================


class Model(models.Model):
    GENDER_CHOICES = [
        ('male', 'ذكر'),
        ('female', 'أنثى'),
    ]

    name = models.CharField(max_length=255, verbose_name="الاسم")
    age = models.PositiveIntegerField(verbose_name="العمر")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="الجنس")
    height = models.CharField(max_length=50, verbose_name="الطول")
    experience = models.CharField(max_length=255, verbose_name="الخبرة",null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف",null=True, blank=True)
    email = models.EmailField(verbose_name="البريد الإلكتروني",null=True, blank=True)

    image_url = models.URLField(blank=True, verbose_name="رابط الصورة")

    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مودل"
        verbose_name_plural = "المودلز"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# =========================
# Content Creator
# =========================
class ContentCreator(models.Model):
    SPECIALTY_CHOICES = [
        ('video', 'محتوى فيديو'),
        ('photo', 'تصوير فوتوغرافي'),
        ('graphics', 'تصميم جرافيكس'),
    ]

    name = models.CharField(max_length=255, verbose_name="الاسم")
    specialty = models.CharField(max_length=50, choices=SPECIALTY_CHOICES, verbose_name="التخصص",null=True, blank=True)
    followers = models.CharField(max_length=50, verbose_name="عدد المتابعين",null=True, blank=True)
    platform = models.CharField(max_length=100, verbose_name="المنصة",null=True, blank=True)
    experience = models.CharField(max_length=255, verbose_name="الخبرة", default='example@example.com',null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف",null=True, blank=True)
    email = models.EmailField(verbose_name="البريد الإلكتروني", default='example@example.com',null=True, blank=True)

    image_url = models.URLField(blank=True, verbose_name="رابط الصورة")

    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "صانع محتوى"
        verbose_name_plural = "صناع المحتوى"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# =========================
# Video Production
# =========================
class VideoProduction(models.Model):
    TYPE_CHOICES = [
        ('commercial', 'إعلاني'),
        ('documentary', 'وثائقي'),
        ('corporate', 'شركات'),
    ]

    name = models.CharField(max_length=255, verbose_name="اسم الفيديو")
    video_type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name="نوع الفيديو")
    duration = models.CharField(max_length=50, verbose_name="المدة")
    quality = models.CharField(max_length=50, verbose_name="الجودة")

    description = models.TextField(blank=True, verbose_name="الوصف")
    video_url = models.URLField(blank=True, verbose_name="رابط الفيديو")
    thumbnail_url = models.URLField(blank=True, verbose_name="رابط الصورة المصغرة")

    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "إنتاج فيديو"
        verbose_name_plural = "إنتاج الفيديو"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# =========================
# Voice Artist
# =========================
class VoiceArtist(models.Model):
    VOICE_TYPE_CHOICES = [
        ('male', 'ذكر'),
        ('female', 'أنثى'),
        ('child', 'طفل'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="الاسم")
    voice_type = models.CharField(max_length=50, choices=VOICE_TYPE_CHOICES, verbose_name="نوع الصوت")
    specialty = models.CharField(max_length=255, verbose_name="التخصص", null=True, blank=True)
    experience = models.CharField(max_length=255, verbose_name="الخبرة",null=True, blank=True)
    languages = models.CharField(max_length=255, verbose_name="اللغات")
    email = models.EmailField(verbose_name="البريد الإلكتروني",null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف", null=True, blank=True)
    audio_sample_url = models.URLField(blank=True, verbose_name="رابط عينة الصوت")
    image_url = models.URLField(blank=True, verbose_name="رابط الصورة")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "فنان صوت"
        verbose_name_plural = "فناني الصوت"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


# =========================
# Content Writing
# =========================
class ContentWriting(models.Model):
    TYPE_CHOICES = [
        ('blog', 'كتابة مدونة'),
        ('social', 'وسائل اجتماعية'),
        ('seo', 'كتابة SEO'),
    ]

    name = models.CharField(max_length=255, verbose_name="الاسم")
    writing_type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name="نوع المحتوى")
    specialty = models.CharField(max_length=255, verbose_name="التخصص", null=True, blank=True)
    experience = models.CharField(max_length=255, verbose_name="الخبرة",null=True, blank=True)
    articles_count = models.PositiveIntegerField(verbose_name="عدد المقالات",null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف",null=True, blank=True)
    email = models.EmailField(verbose_name="البريد الإلكتروني",null=True, blank=True)

    image_url = models.URLField(blank=True, verbose_name="رابط الصورة")

    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "كاتب محتوى"
        verbose_name_plural = "كتابة المحتوى"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# =========================
# Contact Message
# =========================
class ContactMessage(models.Model):
    SERVICE_CHOICES = [
        ('models', 'توفير المودل'),
        ('content-creators', 'صناع المحتوى'),
        ('video-production', 'إنتاج الفيديو'),
        ('voice-artists', 'التعليق الصوتي'),
        ('content-writing', 'كتابة المحتوى'),
    ]

    name = models.CharField(max_length=255, verbose_name="الاسم")
    email = models.EmailField(verbose_name="البريد الإلكتروني",null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف",null=True, blank=True)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, verbose_name="الخدمة")
    message = models.TextField(verbose_name="الرسالة")

    is_read = models.BooleanField(default=False, verbose_name="مقروءة")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "رسالة اتصال"
        verbose_name_plural = "رسائل الاتصال"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.service}"
    
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'مدير'),
        ('provider', 'مزود خدمة'),
        ('management', 'إدارة'),
        ('client', 'عميل'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client', verbose_name="الرتبة")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم الجوال")

    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"