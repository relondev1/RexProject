from django import forms
from .models import Model, ContentCreator, VideoProduction, VoiceArtist, ContentWriting, ContactMessage

class ModelForm(forms.ModelForm):
    class Meta:
        model = Model
        fields = ['name', 'age', 'gender', 'height', 'experience', 'phone', 'email', 'image_url', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'العمر'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'height': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الطول'}),
            'experience': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الخبرة'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'رابط الصورة'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ContentCreatorForm(forms.ModelForm):
    class Meta:
        model = ContentCreator
        fields = ['name', 'specialty', 'followers', 'platform', 'experience', 'phone', 'email', 'image_url', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم'}),
            'specialty': forms.Select(attrs={'class': 'form-control'}),
            'followers': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عدد المتابعين'}),
            'platform': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'المنصة'}),
            'experience': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الخبرة'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'رابط الصورة'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VideoProductionForm(forms.ModelForm):
    class Meta:
        model = VideoProduction
        fields = ['name', 'video_type', 'duration', 'quality', 'description', 'video_url', 'thumbnail_url', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الفيديو'}),
            'video_type': forms.Select(attrs={'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'المدة'}),
            'quality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الجودة'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'الوصف', 'rows': 4}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'رابط الفيديو'}),
            'thumbnail_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'رابط الصورة المصغرة'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VoiceArtistForm(forms.ModelForm):
    class Meta:
        model = VoiceArtist
        fields = ['name', 'voice_type', 'specialty', 'experience', 'languages', 'phone', 'email', 'audio_sample_url', 'image_url', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم'}),
            'voice_type': forms.Select(attrs={'class': 'form-control'}),
            'specialty': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'التخصص'}),
            'experience': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الخبرة'}),
            'languages': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اللغات'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'}),
            'audio_sample_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'رابط عينة صوتية'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'رابط الصورة'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ContentWritingForm(forms.ModelForm):
    class Meta:
        model = ContentWriting
        fields = ['name', 'writing_type', 'specialty', 'experience', 'articles_count', 'phone', 'email', 'image_url', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم'}),
            'writing_type': forms.Select(attrs={'class': 'form-control'}),
            'specialty': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'التخصص'}),
            'experience': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الخبرة'}),
            'articles_count': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عدد المقالات'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'رابط الصورة'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'service', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الكامل'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'تفاصيل الطلب', 'rows': 5}),
        }