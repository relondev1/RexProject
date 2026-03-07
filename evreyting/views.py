from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db import connection
from .forms import ContactMessageForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from functools import wraps
from django.contrib.auth.hashers import make_password
import json
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db import IntegrityError

# ==========================
# دوال مساعدة (Helper Functions)
# ==========================

def dictfetchall(cursor):
    """تحويل cursor rows إلى list of dictionaries"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_user_role(user_id):
    """جلب رتبة المستخدم"""
    if not user_id:
        return None
    with connection.cursor() as cursor:
        cursor.execute("SELECT role FROM evreyting_userprofile WHERE user_id = %s", [user_id])
        row = cursor.fetchone()
        return row[0] if row else None

def admin_required(view_func):
    """ decorator للتحقق من صلاحيات الأدمن"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('services:login')
        
        role = get_user_role(request.user.id)
        if role != 'admin':
            messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة')
            return redirect('services:home')
        return view_func(request, *args, **kwargs)
    return wrapper

# ==========================
# 1. المصادقة والمستخدمين (Auth)
# ==========================

def user_login(request):
    """تسجيل الدخول"""
    if request.user.is_authenticated:
        return redirect('services:home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            
            # التحقق من وجود بروفايل للمستخدم، إذا غير موجود ننشئه
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM evreyting_userprofile WHERE user_id = %s", [user.id])
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO evreyting_userprofile (user_id, role) VALUES (%s, %s)", [user.id, 'client'])
            
            messages.success(request, f'أهلاً بك {user.username}!')
            next_page = request.GET.get('next', 'services:home')
            return redirect(next_page)
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    """تسجيل الخروج"""
    auth_logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح')
    return redirect('services:home')

def signup(request):
    """إنشاء حساب جديد"""
    if request.user.is_authenticated:
        return redirect('services:home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'كلمتا المرور غير متطابقتين')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'اسم المستخدم موجود مسبقاً')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'البريد الإلكتروني مستخدم مسبقاً')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO evreyting_userprofile (user_id, role) VALUES (%s, %s)", [user.id, 'client'])
            auth_login(request, user)
            messages.success(request, 'تم إنشاء الحساب بنجاح!')
            return redirect('services:home')
            
    return render(request, 'registration/signup.html')

# ==========================
# 2. الصفحات الرئيسية والقوائم (General Views)
# ==========================

def home(request):
    """الصفحة الرئيسية"""

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_banner WHERE is_active = TRUE ORDER BY id DESC LIMIT 5")
        banners = dictfetchall(cursor)

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_model WHERE is_active = TRUE ORDER BY created_at DESC LIMIT 6")
        models = dictfetchall(cursor)
        cursor.execute("SELECT * FROM evreyting_contentcreator WHERE is_active = TRUE ORDER BY created_at DESC LIMIT 6")
        creators = dictfetchall(cursor)
        cursor.execute("SELECT * FROM evreyting_videoproduction WHERE is_active = TRUE ORDER BY created_at DESC LIMIT 6")
        productions = dictfetchall(cursor)
        cursor.execute("SELECT * FROM evreyting_voiceartist WHERE is_active = TRUE ORDER BY created_at DESC LIMIT 6")
        artists = dictfetchall(cursor)
        cursor.execute("SELECT * FROM evreyting_contentwriting WHERE is_active = TRUE ORDER BY created_at DESC LIMIT 6")
        writers = dictfetchall(cursor)
        cursor.execute("SELECT * FROM evreyting_siteportfolio WHERE is_active = TRUE ORDER BY created_at DESC LIMIT 6")
        works = dictfetchall(cursor)
    
    context = {
        'models': models, 'creators': creators, 'productions': productions,
        'artists': artists, 'writers': writers, 'works': works,
        'banners': banners,
    }
    return render(request, 'services/home.html', context)

def model_list(request):
    """قائمة المودلز"""
    gender_filter = request.GET.get('gender', '')
    page = int(request.GET.get('page', 1))
    per_page = 12
    offset = (page - 1) * per_page
    
    with connection.cursor() as cursor:
        count_query = "SELECT COUNT(*) FROM evreyting_model WHERE is_active = TRUE"
        params = []
        if gender_filter:
            count_query += " AND gender = %s"
            params.append(gender_filter)
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        query = """SELECT id, name, age, gender, image_url, video_url, is_active, created_at, user_id FROM evreyting_model WHERE is_active = TRUE"""
        data_params = []
        if gender_filter:
            query += " AND gender = %s"
            data_params.append(gender_filter)
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        data_params.extend([per_page, offset])
        
        cursor.execute(query, data_params)
        models = dictfetchall(cursor)
    
    total_pages = (total + per_page - 1) // per_page
    page_obj = {
        'object_list': models, 'number': page,
        'paginator': {'num_pages': total_pages, 'count': total, 'page_range': range(1, total_pages + 1)},
        'has_previous': page > 1, 'has_next': page < total_pages,
        'previous_page_number': page - 1, 'next_page_number': page + 1,
    }
    context = {'page_obj': page_obj, 'gender_filter': gender_filter}
    return render(request, 'services/model_list.html', context)

def content_creator_list(request):
    """قائمة صناع المحتوى"""
    filter_type = request.GET.get('type', '')
    page = int(request.GET.get('page', 1))
    per_page = 12
    offset = (page - 1) * per_page
    
    with connection.cursor() as cursor:
        count_query = "SELECT COUNT(*) FROM evreyting_contentcreator WHERE is_active = TRUE"
        params = []
        if filter_type:
            count_query += " AND platform = %s"
            params.append(filter_type)
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        query = """SELECT id, name, specialty, followers, platform, experience, phone, email, image_url, video_url, is_active, created_at, user_id FROM evreyting_contentcreator WHERE is_active = TRUE"""
        data_params = []
        if filter_type:
            query += " AND platform = %s"
            data_params.append(filter_type)
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        data_params.extend([per_page, offset])
        
        cursor.execute(query, data_params)
        creators = dictfetchall(cursor)
    
    total_pages = (total + per_page - 1) // per_page
    page_obj = {
        'object_list': creators, 'number': page,
        'paginator': {'num_pages': total_pages, 'count': total, 'page_range': range(1, total_pages + 1)},
        'has_previous': page > 1, 'has_next': page < total_pages,
        'previous_page_number': page - 1, 'next_page_number': page + 1,
    }
    context = {'page_obj': page_obj, 'filter_type': filter_type}
    return render(request, 'services/content_creator_list.html', context)

def video_production_list(request):
    """قائمة إنتاج الفيديو"""
    type_filter = request.GET.get('type', '')
    page = int(request.GET.get('page', 1))
    per_page = 12
    offset = (page - 1) * per_page
    
    with connection.cursor() as cursor:
        count_query = "SELECT COUNT(*) FROM evreyting_videoproduction WHERE is_active = TRUE"
        params = []
        if type_filter:
            count_query += " AND video_type = %s"
            params.append(type_filter)
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        query = "SELECT * FROM evreyting_videoproduction WHERE is_active = TRUE"
        if type_filter: query += " AND video_type = %s"
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        productions = dictfetchall(cursor)
    
    total_pages = (total + per_page - 1) // per_page
    page_obj = {'object_list': productions, 'number': page, 'paginator': {'num_pages': total_pages, 'count': total, 'page_range': range(1, total_pages + 1)}, 'has_previous': page > 1, 'has_next': page < total_pages, 'previous_page_number': page - 1, 'next_page_number': page + 1}
    return render(request, 'services/video_production_list.html', {'page_obj': page_obj, 'type_filter': type_filter})

# =========================
# قائمة الفنانين الصوتيين
# =========================
def voice_artist_list(request):
    type_filter = request.GET.get('type', '')
    page = int(request.GET.get('page', 1))
    per_page = 12
    offset = (page - 1) * per_page
    
    with connection.cursor() as cursor:
        # 1. استعلام العد
        count_query = "SELECT COUNT(*) FROM evreyting_voiceartist WHERE is_active = TRUE"
        params = []
        if type_filter:
            count_query += " AND voice_type = %s"
            params.append(type_filter)
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # 2. استعلام جلب البيانات (تم إضافة audio_intro_url و gender)
        query = """
            SELECT id, name, gender, voice_type, languages, specialty, experience, 
                   phone, email, image_url, audio_intro_url, is_active, created_at, user_id
            FROM evreyting_voiceartist 
            WHERE is_active = TRUE
        """
        data_params = []
        if type_filter:
            query += " AND voice_type = %s"
            data_params.append(type_filter)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        data_params.extend([per_page, offset])
        
        cursor.execute(query, data_params)
        artists = dictfetchall(cursor)
    
    
    total_pages = (total + per_page - 1) // per_page
    page_obj = {
        'object_list': artists,
        'number': page,
        'paginator': {
            'num_pages': total_pages,
            'count': total,
            'page_range': range(1, total_pages + 1)
        },
        'has_previous': page > 1,
        'has_next': page < total_pages,
        'previous_page_number': page - 1,
        'next_page_number': page + 1,
    }
    
    context = {
        'page_obj': page_obj,
        'type_filter': type_filter,
    }
    return render(request, 'services/voice_artist_list.html', context)


# =========================
# لوحة تحكم الفنان الصوتي
# =========================

# =========================
# --- الفنانين الصوتيين (Voice) ---
# =========================

@login_required
def voice_dashboard(request):
    target_id, is_admin_view = get_current_target_id(request)
    
    current_role = get_user_role(request.user.id)
    if current_role not in ['admin', 'voice']:
        messages.error(request, 'هذه الصفحة مخصصة للفنانين الصوتيين فقط')
        return redirect('services:home')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_voiceartist WHERE user_id = %s", [target_id])
        data = dictfetchall(cursor)
        instance = data[0] if data else None
        views_count = instance['views'] if instance and instance.get('views') else 0
        cursor.execute("SELECT COUNT(*) FROM evreyting_portfolio WHERE user_id = %s", [target_id])
        portfolio_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM evreyting_chatroom WHERE (client_id = %s OR provider_id = %s) AND status = 'active'", [target_id, target_id])
        chats_count = cursor.fetchone()[0]

    context = {
        'instance': instance, 'profile_views': views_count, 
        'portfolio_count': portfolio_count, 'chats_count': chats_count,
        'is_admin_view': is_admin_view, 'target_user_id': target_id
    }
    return render(request, 'services/voice_dashboard.html', context)

@login_required
def voice_profile_edit(request):
    target_id, is_admin_view = get_current_target_id(request)
    
    current_role = get_user_role(request.user.id)
    is_admin = request.user.is_superuser or current_role == 'admin'
    
    if not is_admin and current_role != 'voice':
        return redirect('services:home')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_voiceartist WHERE user_id = %s", [target_id])
        data = dictfetchall(cursor)
        instance = data[0] if data else None

    if request.method == 'POST':
        name = request.POST.get('name')
        voice_type = request.POST.get('voice_type')
        languages = request.POST.get('languages')
        specialty = request.POST.get('specialty')
        experience = request.POST.get('experience')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        image_url = request.POST.get('image_url')
        audio_intro_url = instance['audio_intro_url'] if instance else None
        
        if 'audio_intro_file' in request.FILES:
            audio_file = request.FILES['audio_intro_file']
            if audio_file.content_type.startswith('audio'):
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'voices'))
                filename = fs.save(f"intro_{target_id}_{audio_file.name}", audio_file)
                audio_intro_url = f"{settings.MEDIA_URL}voices/{filename}"

        with connection.cursor() as cursor:
            if instance:
                cursor.execute("UPDATE evreyting_voiceartist SET name=%s, voice_type=%s, languages=%s, specialty=%s, experience=%s, phone=%s, email=%s, image_url=%s, audio_intro_url=%s WHERE user_id=%s", 
                    [name, voice_type, languages, specialty, experience, phone, email, image_url, audio_intro_url, target_id])
            else:
                cursor.execute("INSERT INTO evreyting_voiceartist (name, voice_type, languages, specialty, experience, phone, email, image_url, audio_intro_url, is_active, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                    [name, voice_type, languages, specialty, experience, phone, email, image_url, audio_intro_url, True, target_id])
        
        messages.success(request, 'تم حفظ المعلومات بنجاح')
        return redirect('services:voice_profile_edit')

    return render(request, 'services/voice_profile_edit.html', {'instance': instance, 'is_admin_view': is_admin_view, 'target_user_id': target_id})

@login_required
def voice_portfolio(request):
    target_id, is_admin_view = get_current_target_id(request)
    
    current_role = get_user_role(request.user.id)
    is_admin = request.user.is_superuser or current_role == 'admin'
    
    if not is_admin and current_role != 'voice':
        return redirect('services:home')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_portfolio WHERE user_id = %s ORDER BY created_at DESC", [target_id])
        portfolio_items = dictfetchall(cursor)

    if request.method == 'POST':
        files = request.FILES.getlist('portfolio_files')
        title = request.POST.get('title', 'عمل صوتي')
        
        if files:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'portfolio'))
            for f in files:
                filename = fs.save(f.name, f)
                file_url = f"{settings.MEDIA_URL}portfolio/{filename}"
                item_type = 'audio'
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO evreyting_portfolio (user_id, title, item_type, media_url) VALUES (%s, %s, %s, %s)", [target_id, title, item_type, file_url])
            messages.success(request, f'تم إضافة {len(files)} أعمال صوتية')
        return redirect('services:voice_portfolio')

    return render(request, 'services/voice_portfolio.html', {'portfolio_items': portfolio_items, 'is_admin_view': is_admin_view, 'target_user_id': target_id})


def content_writing_list(request):
    """قائمة كتابة المحتوى"""
    type_filter = request.GET.get('type', '')
    page = int(request.GET.get('page', 1))
    per_page = 12
    offset = (page - 1) * per_page
    
    with connection.cursor() as cursor:
        count_query = "SELECT COUNT(*) FROM evreyting_contentwriting WHERE is_active = TRUE"
        params = []
        if type_filter:
            count_query += " AND writing_type = %s"
            params.append(type_filter)
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        query = "SELECT id, name, writing_type, specialty, experience, articles_count, phone, email, image_url, is_active, created_at, user_id FROM evreyting_contentwriting WHERE is_active = TRUE"
        if type_filter: query += " AND writing_type = %s"
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        writers = dictfetchall(cursor)
    
    total_pages = (total + per_page - 1) // per_page
    page_obj = {'object_list': writers, 'number': page, 'paginator': {'num_pages': total_pages, 'count': total, 'page_range': range(1, total_pages + 1)}, 'has_previous': page > 1, 'has_next': page < total_pages, 'previous_page_number': page - 1, 'next_page_number': page + 1}
    return render(request, 'services/content_writing_list.html', {'page_obj': page_obj, 'type_filter': type_filter})

# ==========================
# 3.  والطلبات
# ==========================

@login_required
def request_service(request):
    """طلب خدمة"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM evreyting_userprofile WHERE user_id = %s", [request.user.id])
        if not cursor.fetchone():
            cursor.execute("INSERT INTO evreyting_userprofile (user_id, role) VALUES (%s, %s)", [request.user.id, 'client'])

    service_name = request.GET.get('service', '')
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO evreyting_contactmessage (name, email, phone, service, message, is_read, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())", [data['name'], data['email'], data['phone'], data['service'], data['message'], False])
            messages.success(request, 'تم إرسال طلب الخدمة بنجاح')
            return redirect('services:home')
    else:
        initial = {'service': service_name, 'name': request.user.get_full_name() or request.user.username, 'email': getattr(request.user, 'email', '')}
        form = ContactMessageForm(initial=initial)
    return render(request, 'services/request_service.html', {'form': form, 'service_name': service_name})

# ==========================
# 4. لوحات تحكم مقدمي الخدمة (Dashboards)
# ==========================

def get_current_target_id(request):
    """تحديد معرف المستخدم المستهدف (من الجلسة للأدمن، أو من الحساب الشخصي)"""
    if request.session.get('admin_control_id'):
        return int(request.session['admin_control_id']), True
    return request.user.id, False

# === دالة الدخول (التي يضغط عليها الأدمن) ===
@login_required
def admin_open_panel(request, user_id):
    """دخول الأدمن على لوحة تحكم أي مستخدم"""
    is_admin = request.user.is_superuser or (get_user_role(request.user.id) == 'admin')
    if not is_admin:
        return redirect('services:home')
    
    request.session['admin_control_id'] = user_id
    
    target_role = get_user_role(user_id)
    
    # توجيه الرابط حسب نوع المستخدم
    if target_role == 'model':
        return redirect('services:model_dashboard')
    elif target_role == 'creator':
        return redirect('services:creator_dashboard')
    elif target_role == 'voice':
        return redirect('services:voice_dashboard')
    elif target_role == 'videographer':
        return redirect('services:video_dashboard') # إذا كانت الدالة موجودة
    elif target_role == 'writer':
        return redirect('services:writer_dashboard') # إذا كانت الدالة موجودة
    else:
        messages.warning(request, "هذا المستخدم ليس لديه لوحة تحكم خاصة")
        return redirect('services:admin_users')

# === دالة الخروج ===
@login_required
def admin_close_panel(request):
    if 'admin_control_id' in request.session:
        del request.session['admin_control_id']
    return redirect('services:admin_users')


# =========================
# --- المودلز (Model) ---
# =========================

@login_required
def model_dashboard(request):
    # 1. تحديد المستخدم (إذا أدمن يأخذ من الجلسة، إذا عادي يأخذ حسابه)
    target_id, is_admin_view = get_current_target_id(request)
    
    # 2. التحقق من الصلاحية (يسمح فقط للأدمن أو المودل)
    current_role = get_user_role(request.user.id)
    if current_role not in ['admin', 'model']:
        messages.error(request, 'هذه الصفحة مخصصة للمودلز فقط')
        return redirect('services:home')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_model WHERE user_id = %s", [target_id])
        data = dictfetchall(cursor)
        instance = data[0] if data else None
        views_count = instance['views'] if instance and instance.get('views') else 0
        cursor.execute("SELECT COUNT(*) FROM evreyting_portfolio WHERE user_id = %s", [target_id])
        portfolio_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM evreyting_chatroom WHERE (client_id = %s OR provider_id = %s) AND status = 'active'", [target_id, target_id])
        chats_count = cursor.fetchone()[0]

    context = {
        'instance': instance, 
        'profile_views': views_count, 
        'portfolio_count': portfolio_count, 
        'chats_count': chats_count,
        'is_admin_view': is_admin_view, 
        'target_user_id': target_id 
    }
    return render(request, 'services/model_dashboard.html', context)

@login_required
def model_profile_edit(request):
    target_id, is_admin_view = get_current_target_id(request)
    
    current_role = get_user_role(request.user.id)
    if current_role not in ['admin', 'model']:
        return redirect('services:home')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_model WHERE user_id = %s", [target_id])
        data = dictfetchall(cursor)
        instance = data[0] if data else None

    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age') or None
        gender = request.POST.get('gender')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        eye_color = request.POST.get('eye_color')
        hair_color = request.POST.get('hair_color')
        image_url = request.POST.get('image_url')
        video_url = instance['video_url'] if instance else None

        if 'video_file' in request.FILES:
            video_file = request.FILES['video_file']
            if video_file.content_type.startswith('video'):
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'videos'))
                filename = fs.save(f"model_{target_id}_{video_file.name}", video_file)
                video_url = f"{settings.MEDIA_URL}videos/{filename}"

        with connection.cursor() as cursor:
            if instance:
                cursor.execute("UPDATE evreyting_model SET name=%s, age=%s, gender=%s, height=%s, weight=%s, eye_color=%s, hair_color=%s, image_url=%s, video_url=%s WHERE user_id=%s", 
                    [name, age, gender, height, weight, eye_color, hair_color, image_url, video_url, target_id])
            else:
                cursor.execute("INSERT INTO evreyting_model (name, age, gender, height, weight, eye_color, hair_color, image_url, video_url, is_active, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                    [name, age, gender, height, weight, eye_color, hair_color, image_url, video_url, True, target_id])
        
        messages.success(request, 'تم حفظ المعلومات بنجاح')
        return redirect('services:model_profile_edit')

    return render(request, 'services/model_profile_edit.html', {'model_instance': instance, 'is_admin_view': is_admin_view, 'target_user_id': target_id})

@login_required
def model_portfolio(request):
    target_id, is_admin_view = get_current_target_id(request)
    
    current_role = get_user_role(request.user.id)
    if current_role not in ['admin', 'model']:
        return redirect('services:home')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_portfolio WHERE user_id = %s ORDER BY created_at DESC", [target_id])
        portfolio_items = dictfetchall(cursor)

    if request.method == 'POST':
        files = request.FILES.getlist('portfolio_files')
        if files:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'portfolio'))
            for f in files:
                filename = fs.save(f.name, f)
                file_url = f"{settings.MEDIA_URL}portfolio/{filename}"
                ext = os.path.splitext(f.name)[1].lower()
                item_type = 'image' if ext in ['.jpg', '.jpeg', '.png', '.gif'] else 'video'
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO evreyting_portfolio (user_id, title, item_type, media_url) VALUES (%s, %s, %s, %s)", [target_id, f.name, item_type, file_url])
            messages.success(request, f'تم إضافة {len(files)} عناصر')
        return redirect('services:model_portfolio')

    return render(request, 'services/model_portfolio.html', {'portfolio_items': portfolio_items, 'is_admin_view': is_admin_view, 'target_user_id': target_id})

# --- صناع المحتوى ---
# =========================
# --- صناع المحتوى (Creator) ---
# =========================

@login_required
def creator_dashboard(request):
    target_id, is_admin_view = get_current_target_id(request)
    
    current_role = get_user_role(request.user.id)
    # السماح للأدمن أو لصانع المحتوى
    if current_role not in ['admin', 'creator']:
        messages.error(request, 'هذه الصفحة مخصصة لصناع المحتوى فقط')
        return redirect('services:home')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_contentcreator WHERE user_id = %s", [target_id])
        data = dictfetchall(cursor)
        instance = data[0] if data else None
        views_count = instance['views'] if instance and instance.get('views') else 0
        cursor.execute("SELECT COUNT(*) FROM evreyting_portfolio WHERE user_id = %s", [target_id])
        portfolio_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM evreyting_chatroom WHERE (client_id = %s OR provider_id = %s) AND status = 'active'", [target_id, target_id])
        chats_count = cursor.fetchone()[0]

    context = {
        'instance': instance, 'profile_views': views_count, 
        'portfolio_count': portfolio_count, 'chats_count': chats_count,
        'is_admin_view': is_admin_view, 'target_user_id': target_id
    }
    return render(request, 'services/creator_dashboard.html', context)

@login_required
def creator_profile_edit(request):
    target_id, is_admin_view = get_current_target_id(request)
    
    current_role = get_user_role(request.user.id)
    if current_role not in ['admin', 'creator']:
        return redirect('services:home')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_contentcreator WHERE user_id = %s", [target_id])
        data = dictfetchall(cursor)
        instance = data[0] if data else None

    if request.method == 'POST':
        form_data = {
            'name': request.POST.get('name'), 'age': request.POST.get('age') or None,
            'gender': request.POST.get('gender'), 'platform': request.POST.get('platform'),
            'followers': request.POST.get('followers'), 'specialty': request.POST.get('specialty'),
            'experience': request.POST.get('experience'), 'image_url': request.POST.get('image_url'),
            'user_id': target_id
        }
        video_url = instance['video_url'] if instance else None
        if 'video_file' in request.FILES:
            video_file = request.FILES['video_file']
            if video_file.content_type.startswith('video'):
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'videos'))
                filename = fs.save(f"creator_{target_id}_{video_file.name}", video_file)
                video_url = f"{settings.MEDIA_URL}videos/{filename}"
        form_data['video_url'] = video_url

        with connection.cursor() as cursor:
            if instance:
                cursor.execute("UPDATE evreyting_contentcreator SET name=%(name)s, age=%(age)s, gender=%(gender)s, platform=%(platform)s, followers=%(followers)s, specialty=%(specialty)s, experience=%(experience)s, image_url=%(image_url)s, video_url=%(video_url)s WHERE user_id=%(user_id)s", form_data)
            else:
                cursor.execute("INSERT INTO evreyting_contentcreator (name, age, gender, platform, followers, specialty, experience, image_url, video_url, is_active, user_id) VALUES (%(name)s, %(age)s, %(gender)s, %(platform)s, %(followers)s, %(specialty)s, %(experience)s, %(image_url)s, %(video_url)s, TRUE, %(user_id)s)", form_data)
        
        messages.success(request, 'تم حفظ المعلومات بنجاح')
        return redirect('services:creator_profile_edit')

    return render(request, 'services/creator_profile_edit.html', {'instance': instance, 'is_admin_view': is_admin_view, 'target_user_id': target_id})

@login_required
def creator_portfolio(request):
    target_id, is_admin_view = get_current_target_id(request)
    
    current_role = get_user_role(request.user.id)
    if current_role not in ['admin', 'creator']:
        return redirect('services:home')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_portfolio WHERE user_id = %s ORDER BY created_at DESC", [target_id])
        portfolio_items = dictfetchall(cursor)

    if request.method == 'POST':
        files = request.FILES.getlist('portfolio_files')
        if files:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'portfolio'))
            for f in files:
                filename = fs.save(f.name, f)
                file_url = f"{settings.MEDIA_URL}portfolio/{filename}"
                ext = os.path.splitext(f.name)[1].lower()
                item_type = 'image' if ext in ['.jpg', '.jpeg', '.png', '.gif'] else 'video'
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO evreyting_portfolio (user_id, title, item_type, media_url) VALUES (%s, %s, %s, %s)", [target_id, f.name, item_type, file_url])
            messages.success(request, f'تم إضافة {len(files)} عناصر')
        return redirect('services:creator_portfolio')

    return render(request, 'services/creator_portfolio.html', {'portfolio_items': portfolio_items, 'is_admin_view': is_admin_view, 'target_user_id': target_id})

# --- لوحات تحكم أخرى (مختصرة) ---
@login_required
def video_dashboard(request):
    role = get_user_role(request.user.id)
    if role != 'videographer':
        messages.error(request, 'هذه الصفحة مخصصة لمنتجي الفيديو فقط')
        return redirect('services:home')
    # ... (يمكن إضافة المنطق هنا كما في model_dashboard إذا كانت هناك بيانات خاصة) ...
    return render(request, 'services/provider_dashboard.html', {'role': 'منتج فيديو'})

@login_required
def voice_dashboard(request):
    target_id, is_admin_view = get_current_target_id(request)
    
    # التحقق المحسن: السماح للأدمن (حتى لو لم يكن لديه ملف شخصي) أو لفنان الصوتي
    current_role = get_user_role(request.user.id)
    is_admin = request.user.is_superuser or current_role == 'admin'
    
    if not is_admin and current_role != 'voice':
        messages.error(request, 'هذه الصفحة مخصصة للفنانين الصوتيين فقط')
        return redirect('services:home')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_voiceartist WHERE user_id = %s", [target_id])
        data = dictfetchall(cursor)
        instance = data[0] if data else None
        views_count = instance['views'] if instance and instance.get('views') else 0
        cursor.execute("SELECT COUNT(*) FROM evreyting_portfolio WHERE user_id = %s", [target_id])
        portfolio_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM evreyting_chatroom WHERE (client_id = %s OR provider_id = %s) AND status = 'active'", [target_id, target_id])
        chats_count = cursor.fetchone()[0]

    context = {
        'instance': instance, 'profile_views': views_count, 
        'portfolio_count': portfolio_count, 'chats_count': chats_count,
        'is_admin_view': is_admin_view, 'target_user_id': target_id
    }
    return render(request, 'services/voice_dashboard.html', context)

@login_required
def writer_dashboard(request):
    role = get_user_role(request.user.id)
    if role != 'writer':
        messages.error(request, 'هذه الصفحة مخصصة للكتّاب فقط')
        return redirect('services:home')
    return render(request, 'services/provider_dashboard.html', {'role': 'كاتب محتوى'})


# ==========================
# 5. الملفات الشخصية (Profiles)
# ==========================

def provider_profile(request, user_id):
    """صفحة الملف الشخصي للمودل أو صانع المحتوى أو الفنان الصوتي"""
    try:
        user_obj = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('services:home')

    role = get_user_role(user_id)
    profile_data = None
    
    with connection.cursor() as cursor:
        # 1. جلب البيانات حسب الدور
        if role == 'model':
            cursor.execute("SELECT * FROM evreyting_model WHERE user_id = %s", [user_id])
            data = dictfetchall(cursor)
            profile_data = data[0] if data else None
            # زيادة المشاهدات
            if profile_data and (not request.user.is_authenticated or request.user.id != user_id):
                cursor.execute("UPDATE evreyting_model SET views = views + 1 WHERE user_id = %s", [user_id])
        
        elif role == 'creator':
            cursor.execute("SELECT * FROM evreyting_contentcreator WHERE user_id = %s", [user_id])
            data = dictfetchall(cursor)
            profile_data = data[0] if data else None
            # زيادة المشاهدات
            if profile_data and (not request.user.is_authenticated or request.user.id != user_id):
                cursor.execute("UPDATE evreyting_contentcreator SET views = views + 1 WHERE user_id = %s", [user_id])
        
        # === جديد: دعم الفنانين الصوتيين ===
        elif role == 'voice':
            cursor.execute("SELECT * FROM evreyting_voiceartist WHERE user_id = %s", [user_id])
            data = dictfetchall(cursor)
            profile_data = data[0] if data else None
            # زيادة المشاهدات
            if profile_data and (not request.user.is_authenticated or request.user.id != user_id):
                cursor.execute("UPDATE evreyting_voiceartist SET views = views + 1 WHERE user_id = %s", [user_id])
        
        # 2. جلب معرض الأعمال (مشترك)
        cursor.execute("SELECT * FROM evreyting_portfolio WHERE user_id = %s ORDER BY created_at DESC", [user_id])
        portfolio_items = dictfetchall(cursor)

    context = {
        'provider_user': user_obj,
        'role': role,
        'profile_data': profile_data,
        'portfolio_items': portfolio_items
    }
    return render(request, 'services/provider_profile.html', context)

@login_required
def provider_portal(request):
    """لوحة تحكم موحدة لمقدمي الخدمة"""
    role = get_user_role(request.user.id)
    if role not in ['provider', 'admin', 'management']: 
        messages.error(request, 'هذه اللوحة مخصصة لمقدمي الخدمات فقط')
        return redirect('services:home')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, title, description, item_type, media_url, created_at FROM evreyting_portfolio WHERE user_id = %s ORDER BY created_at DESC", [request.user.id])
        portfolio_items = dictfetchall(cursor)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        item_type = request.POST.get('item_type')
        media_url = request.POST.get('media_url')
        if title and media_url and item_type:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO evreyting_portfolio (user_id, title, description, item_type, media_url) VALUES (%s, %s, %s, %s, %s)", [request.user.id, title, description, item_type, media_url])
            messages.success(request, 'تمت إضافة العمل بنجاح')
            return redirect('services:provider_portal')

    return render(request, 'services/provider_portal.html', {'portfolio_items': portfolio_items, 'role': role})

@login_required
def delete_portfolio_item(request, item_id):
    """حذف عنصر من المعرض (يدعم وضع الأدمن)"""
    
    # 1. تحديد المستخدم المستهدف (إذا أدمن يأخذ من الجلسة)
    target_id, is_admin_view = get_current_target_id(request)
    
    # 2. التحقق من الصلاحيات (يسمح فقط للأدمن أو صاحب الملف)
    current_role = get_user_role(request.user.id)
    if current_role not in ['admin', 'model', 'creator']: # أضف الأدوار الأخرى إذا لزم
        return redirect('services:home')

    with connection.cursor() as cursor:
        # التحقق أن العنصر يتبع المستخدم المستهدف
        cursor.execute("SELECT user_id FROM evreyting_portfolio WHERE id = %s", [item_id])
        item = cursor.fetchone()
        
        if item and item[0] == target_id:
            cursor.execute("DELETE FROM evreyting_portfolio WHERE id = %s", [item_id])
            messages.success(request, 'تم حذف العمل بنجاح')
        else:
            messages.error(request, 'لا تملك صلاحية لحذف هذا العمل')
            
    # العودة للصفحة السابقة
    return redirect(request.META.get('HTTP_REFERER', 'services:home'))

# ==========================
# 6. المحادثات (Chat)
# ==========================

@login_required
def start_chat(request, provider_id):
    if request.user.id == provider_id:
        messages.error(request, "لا يمكنك فتح محادثة مع نفسك")
        return redirect('services:home')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM evreyting_chatroom WHERE (client_id = %s AND provider_id = %s) OR (client_id = %s AND provider_id = %s) LIMIT 1", [request.user.id, provider_id, provider_id, request.user.id])
        room = cursor.fetchone()

        if room:
            return redirect('services:chat_room', room_id=room[0])
        else:
            cursor.execute("INSERT INTO evreyting_chatroom (client_id, provider_id, status) VALUES (%s, %s, 'active')", [request.user.id, provider_id])
            new_room_id = cursor.lastrowid
            return redirect('services:chat_room', room_id=new_room_id)

@login_required
def chat_room(request, room_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_chatroom WHERE id = %s", [room_id])
        room_data = dictfetchall(cursor)
        if not room_data: return redirect('services:home')
        room = room_data[0]
        
        if request.user.id != room['client_id'] and request.user.id != room['provider_id']:
            return redirect('services:home')

        other_id = room['provider_id'] if request.user.id == room['client_id'] else room['client_id']
        cursor.execute("SELECT id, username FROM auth_user WHERE id = %s", [other_id])
        other_user = dictfetchall(cursor)[0]

        cursor.execute("SELECT cm.*, u.username as sender_name, up.role as sender_role FROM evreyting_chatmessage cm LEFT JOIN auth_user u ON cm.sender_id = u.id LEFT JOIN evreyting_userprofile up ON cm.sender_id = up.user_id WHERE cm.room_id = %s ORDER BY cm.created_at ASC", [room_id])
        messages = dictfetchall(cursor)
        last_id = messages[-1]['id'] if messages else 0

    context = {'room_id': room_id, 'other_user': other_user, 'messages': messages, 'last_id': last_id, 'current_user_id': request.user.id}
    return render(request, 'services/chat_room.html', context)

@login_required
def send_message(request):
    """إرسال رسالة"""
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        content = request.POST.get('content')
        
        if content and room_id:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO evreyting_chatmessage 
                        (room_id, sender_id, content, status, is_read, created_at)
                        VALUES (%s, %s, %s, 'sent', 0, NOW())
                    """, [room_id, request.user.id, content])
                    new_id = cursor.lastrowid
                
                return JsonResponse({'status': 'success', 'message_id': new_id})
            except Exception as e:
                print(f"Error sending message: {e}")
                return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error'})

def get_messages_api(request, room_id):
    last_id = request.GET.get('last_id', 0)
    with connection.cursor() as cursor:
        cursor.execute("SELECT cm.id, cm.sender_id, cm.content, cm.created_at, u.username, up.role FROM evreyting_chatmessage cm LEFT JOIN auth_user u ON cm.sender_id = u.id LEFT JOIN evreyting_userprofile up ON cm.sender_id = up.user_id WHERE cm.room_id = %s AND cm.id > %s ORDER BY cm.created_at ASC", [room_id, last_id])
        messages_data = dictfetchall(cursor)
    
    data = {'messages': [{'id': m['id'], 'sender_id': m['sender_id'], 'content': m['content'], 'time': m['created_at'].strftime('%I:%M %p') if m['created_at'] else '', 'sender_name': m['username'], 'role': m['role']} for m in messages_data]}
    return JsonResponse(data)

@login_required
def my_chats(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT c.id, c.created_at, c.status, u1.username as client_name, u2.username as provider_name, (SELECT content FROM evreyting_chatmessage WHERE room_id = c.id ORDER BY created_at DESC LIMIT 1) as last_msg FROM evreyting_chatroom c JOIN auth_user u1 ON c.client_id = u1.id JOIN auth_user u2 ON c.provider_id = u2.id WHERE c.client_id = %s OR c.provider_id = %s ORDER BY c.created_at DESC", [request.user.id, request.user.id])
        chats = dictfetchall(cursor)
    return render(request, 'services/my_chats.html', {'chats': chats})

# ==========================
# 7. لوحة تحكم الأدمن (Admin Panel)
# ==========================

@admin_required
def admin_dashboard(request):
    """الصفحة الرئيسية للوحة التحكم"""
    with connection.cursor() as cursor:
        # 1. إجمالي المستخدمين (النشطين فقط، بدون المحذوفين)
        cursor.execute("SELECT COUNT(*) FROM auth_user WHERE is_active = TRUE")
        users_count = cursor.fetchone()[0]
        
        # 2. الطلبات الجديدة (رسائل التواصل غير المقروءة)
        cursor.execute("SELECT COUNT(*) FROM evreyting_contactmessage WHERE is_read = FALSE")
        new_requests = cursor.fetchone()[0]
        
        # 3. إجمالي المحادثات (كل المحادثات الموجودة في الموقع)
        cursor.execute("SELECT COUNT(*) FROM evreyting_chatroom")
        total_chats = cursor.fetchone()[0]

    context = {
        'users_count': users_count,
        'new_requests': new_requests,
        'total_chats': total_chats,
    }
    return render(request, 'services/admin_dashboard.html', context)

@admin_required
def admin_users(request):
    """إدارة المستخدمين"""
    with connection.cursor() as cursor:
        # تم تعديل الاستعلام: أزلنا WHERE u.is_active = TRUE
        # لنظهر المستخدمين النشطين والموقوفين (ولكن ليس المحذوفين تماماً إذا أضفنا شرطاً لذلك)
        # حالياً سنظهر الجميع عدا من تم أرشفتهم
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.is_active, u.first_name, up.role 
            FROM auth_user u 
            LEFT JOIN evreyting_userprofile up ON u.id = up.user_id
            WHERE u.username NOT LIKE '%_archived_%'
            ORDER BY u.id DESC
        """)
        users = dictfetchall(cursor)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'client')
        
        if username and password:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO evreyting_userprofile (user_id, role) VALUES (%s, %s)", [user.id, role])
                messages.success(request, 'تم إنشاء المستخدم بنجاح')
                return redirect('services:admin_users')

            except IntegrityError:
                try:
                    old_user = User.objects.get(username=username)
                    
                    if not old_user.is_active:
                        # إذا كان الاسم لمستخدم محذوف سابقاً، نغير اسمه ونحرر الاسم الجديد
                        old_user.username = f"{username}_archived_{old_user.id}"
                        old_user.save()
                        
                        user = User.objects.create_user(username=username, email=email, password=password)
                        with connection.cursor() as cursor:
                            cursor.execute("INSERT INTO evreyting_userprofile (user_id, role) VALUES (%s, %s)", [user.id, role])
                        
                        messages.success(request, 'تم إنشاء المستخدم بنجاح (تم تحرير الاسم من حساب مؤرشف)')
                        return redirect('services:admin_users')
                    else:
                        messages.error(request, 'اسم المستخدم موجود مسبقاً ومستخدم حالياً')
                
                except Exception as e:
                    messages.error(request, f'حدث خطأ غير متوقع: {str(e)}')

    context = {'users': users}
    return render(request, 'services/admin_users.html', context)

@admin_required
def admin_edit_user(request, user_id):
    """تعديل بيانات مستخدم"""
    
    # منع التعديل على النفس
    if request.user.id == user_id:
        messages.error(request, 'لا يمكنك تعديل بيانات حسابك الخاص من هنا!')
        return redirect('services:admin_users')

    # جلب البيانات الحالية
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.username, u.email, u.first_name, u.is_staff, up.role, up.phone
            FROM auth_user u
            LEFT JOIN evreyting_userprofile up ON u.id = up.user_id
            WHERE u.id = %s
        """, [user_id])
        user_data = cursor.fetchone()

    if not user_data:
        messages.error(request, 'المستخدم غير موجود')
        return redirect('services:admin_users')

    # تجهيز البيانات للقالب
    context = {
        'user_id': user_id,
        'username': user_data[0],
        'email': user_data[1],
        'first_name': user_data[2] or '',
        'is_staff': user_data[3],
        'role': user_data[4] or 'client',
        'phone': user_data[5] or '',
    }

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        role = request.POST.get('role')
        phone = request.POST.get('phone', '')
        new_password = request.POST.get('password')

        try:
            # 1. تحديث جدول auth_user
            user = User.objects.get(id=user_id)
            user.username = username
            user.email = email
            user.first_name = first_name
            
            if new_password: # إذا تم إدخال كلمة مرور جديدة
                user.password = make_password(new_password)
            
            # محاولة الحفظ مع معالجة تكرار الاسم
            try:
                user.save()
            except IntegrityError:
                # الاسم مكرر، نتحقق من صاحب الاسم الآخر
                try:
                    other_user = User.objects.get(username=username)
                    
                    if not other_user.is_active:
                        # المستخدم الآخر محذوف (معطل)، نغير اسمه ونحرر الاسم الحالي
                        other_user.username = f"{username}_archived_{other_user.id}"
                        other_user.save()
                        user.save() # نحاول حفظ المستخدم الحالي مرة أخرى
                        messages.success(request, 'تم تحديث الاسم (تم تحريره من حساب محذوف سابق)')
                    else:
                        # المستخدم الآخر نشط ومستخدم حالياً
                        messages.error(request, 'اسم المستخدم موجود مسبقاً ومستخدم حالياً')
                        return render(request, 'services/admin_edit_user.html', context)
                        
                except User.DoesNotExist:
                    # حالة نادرة، نحاول الحفظ مباشرة
                    user.save()

            # 2. تحديث جدول evreyting_userprofile باستخدام SQL
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE evreyting_userprofile 
                    SET role = %s, phone = %s 
                    WHERE user_id = %s
                """, [role, phone, user_id])
                
                # إذا لم يتم تحديث أي صف (ليس له بروفايل)، ننشئ واحد جديد
                if cursor.rowcount == 0:
                    cursor.execute("""
                        INSERT INTO evreyting_userprofile (user_id, role, phone) 
                        VALUES (%s, %s, %s)
                    """, [user_id, role, phone])

            messages.success(request, 'تم تحديث بيانات المستخدم بنجاح')
            return redirect('services:admin_users')
            
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')

    return render(request, 'services/admin_edit_user.html', context)

@admin_required
def admin_delete_user(request, user_id):
    """حذف المستخدم نهائياً (إيقاف دخول + إخفاء ملف + حذف أعمال + إخفاء من قائمة الأدمن)"""
    
    if request.user.id == user_id:
        messages.error(request, 'لا يمكنك حذف حسابك الخاص!')
        return redirect('services:admin_users')
    
    try:
        # نجلب بيانات المستخدم أولاً لمعرفة اسمه
        user = User.objects.get(id=user_id)
        current_username = user.username
        
        with connection.cursor() as cursor:
            # 1. تعطيل الحساب وتغيير الاسم ليصبح "مؤرشف" (ليختفي من قائمة الأدمن)
            # تغيير الاسم يحقق هدفين: يختفي من القائمة، ويحرر الاسم للتسجيل به مجدداً
            new_archived_name = f"{current_username}_archived_{user_id}"
            cursor.execute("UPDATE auth_user SET is_active = FALSE, username = %s WHERE id = %s", [new_archived_name, user_id])
            
            # 2. إخفاء الملف الشخصي من قوالب الموقع
            tables_to_hide = [
                'evreyting_model', 
                'evreyting_contentcreator', 
                'evreyting_videoproduction', 
                'evreyting_voiceartist', 
                'evreyting_contentwriting'
            ]
            for table in tables_to_hide:
                cursor.execute(f"UPDATE {table} SET is_active = FALSE WHERE user_id = %s", [user_id])
            
            # 3. حذف الأعمال من المعرض
            cursor.execute("DELETE FROM evreyting_portfolio WHERE user_id = %s", [user_id])
        
        messages.success(request, 'تم حذف المستخدم وتصفية حسابه بالكامل')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء الحذف: {str(e)}')
        
    return redirect('services:admin_users')

@admin_required
def admin_toggle_user(request, user_id):
    """إيقاف / تفعيل المستخدم (مؤقتاً - بدون حذف البيانات)"""
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            
            # تغيير حالة التفعيل فقط
            user.is_active = not user.is_active
            user.save()
            
            status = "تفعيل" if user.is_active else "إيقاف"
            messages.success(request, f'تم {status} الحساب بنجاح. يمكن للمستخدم الدخول الآن.' if user.is_active else f'تم إيقاف الحساب. لن يتمكن المستخدم من الدخول.')
            
        except User.DoesNotExist:
            messages.error(request, 'المستخدم غير موجود')
            
    return redirect('services:admin_users')

@admin_required
def admin_messages(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_contactmessage ORDER BY created_at DESC")
        messages_list = dictfetchall(cursor)
    return render(request, 'services/admin_messages.html', {'messages_list': messages_list})

@admin_required
def admin_portfolio(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_siteportfolio ORDER BY created_at DESC")
        items = dictfetchall(cursor)
    if request.method == 'POST':
        title = request.POST.get('title')
        media_type = request.POST.get('media_type')
        media_url = request.POST.get('media_url')
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO evreyting_siteportfolio (title, media_type, media_url) VALUES (%s, %s, %s)", [title, media_type, media_url])
        messages.success(request, 'تمت إضافة العمل بنجاح')
        return redirect('services:admin_portfolio')
    return render(request, 'services/admin_portfolio.html', {'items': items})

@admin_required
def admin_delete_portfolio(request, item_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM evreyting_siteportfolio WHERE id = %s", [item_id])
    messages.success(request, 'تم حذف العمل')
    return redirect('services:admin_portfolio')

@admin_required
def admin_requests(request):
    with connection.cursor() as cursor:
        query = "SELECT cr.id, cr.client_id, cr.provider_id, cr.status, cr.created_at, cm.content as last_message, cm.created_at as last_message_time, u1.username as client_name, u2.username as provider_name FROM evreyting_chatroom cr LEFT JOIN evreyting_chatmessage cm ON cr.id = cm.room_id AND cm.id = (SELECT MAX(id) FROM evreyting_chatmessage WHERE room_id = cr.id) LEFT JOIN auth_user u1 ON cr.client_id = u1.id LEFT JOIN auth_user u2 ON cr.provider_id = u2.id ORDER BY COALESCE(cm.created_at, cr.created_at) DESC"
        cursor.execute(query)
        chats = dictfetchall(cursor)
    return render(request, 'services/admin_requests.html', {'chats': chats})

@admin_required
def admin_chat_view(request, room_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT cr.*, u1.username as client_name, u2.username as provider_name FROM evreyting_chatroom cr LEFT JOIN auth_user u1 ON cr.client_id = u1.id LEFT JOIN auth_user u2 ON cr.provider_id = u2.id WHERE cr.id = %s", [room_id])
        room_data = dictfetchall(cursor)
        if not room_data: return redirect('services:admin_requests')
        room = room_data[0]

        cursor.execute("SELECT cm.*, u.username as sender_name, up.role as sender_role FROM evreyting_chatmessage cm LEFT JOIN auth_user u ON cm.sender_id = u.id LEFT JOIN evreyting_userprofile up ON cm.sender_id = up.user_id WHERE cm.room_id = %s ORDER BY cm.created_at ASC", [room_id])
        messages = dictfetchall(cursor)
        last_id = messages[-1]['id'] if messages else 0

    context = {'room': room, 'messages': messages, 'last_id': last_id, 'current_user_id': request.user.id}
    return render(request, 'services/admin_chat_view.html', context)

@admin_required
def admin_send_message(request):
    if request.method == 'POST' and request.user.is_authenticated:
        room_id = request.POST.get('room_id')
        content = request.POST.get('content')
        if content:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO evreyting_chatmessage (room_id, sender_id, content, status) VALUES (%s, %s, %s, 'sent')", [room_id, request.user.id, content])
                new_id = cursor.lastrowid
            return JsonResponse({'status': 'success', 'message_id': new_id})
    return JsonResponse({'status': 'error'})

# === إدارة البنرات ===
@admin_required
def admin_banners(request):
    """إدارة البنرات"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM evreyting_banner ORDER BY id DESC")
        banners = dictfetchall(cursor)
    
    if request.method == 'POST':
        title = request.POST.get('title', '')
        image_url = request.POST.get('image_url')
        link_url = request.POST.get('link_url', '#')
        
        if image_url:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO evreyting_banner (title, image_url, link_url, is_active) VALUES (%s, %s, %s, 1)", [title, image_url, link_url])
            messages.success(request, 'تمت إضافة البنر بنجاح')
            return redirect('services:admin_banners')
            
    return render(request, 'services/admin_banners.html', {'banners': banners})

@admin_required
def admin_toggle_banner(request, banner_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE evreyting_banner SET is_active = NOT is_active WHERE id = %s", [banner_id])
    messages.success(request, 'تم تحديث حالة البنر')
    return redirect('services:admin_banners')

@admin_required
def admin_delete_banner(request, banner_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM evreyting_banner WHERE id = %s", [banner_id])
    messages.success(request, 'تم حذف البنر')
    return redirect('services:admin_banners')

# === لوحة تحكم الأدمن لمستخدم محدد ===
@admin_required
def admin_user_panel(request, user_id):
    """
    هذه الدالة تتيح للأدمن الدخول على لوحة تحكم المستخدم
    وعرض بياناته (مثل لوحة تحكم المودل/الصانع) والتحكم فيها.
    """
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "المستخدم غير موجود")
        return redirect('services:admin_users')

    role = get_user_role(user_id)
    profile_data = None
    
    with connection.cursor() as cursor:
        # جلب البيانات حسب الدور
        if role == 'model':
            cursor.execute("SELECT * FROM evreyting_model WHERE user_id = %s", [user_id])
            data = dictfetchall(cursor)
            profile_data = data[0] if data else None
            template_name = 'services/model_dashboard.html'
            
        elif role == 'creator':
            cursor.execute("SELECT * FROM evreyting_contentcreator WHERE user_id = %s", [user_id])
            data = dictfetchall(cursor)
            profile_data = data[0] if data else None
            template_name = 'services/creator_dashboard.html'
            
        # يمكنك إضافة باقي الأدوار هنا...
        
        else:
            # إذا كان عميل أو دور عام، نعرض صفحة بسيطة أو نرجعه للتعديل العادي
            messages.info(request, "هذا المستخدم ليس لديه لوحة تحكم خاصة (عميل). يمكنك تعديل بياناته الأساسية.")
            return redirect('services:admin_edit_user', user_id=user_id)

        # جلب معرض الأعمال
        cursor.execute("SELECT * FROM evreyting_portfolio WHERE user_id = %s ORDER BY created_at DESC", [user_id])
        portfolio_items = dictfetchall(cursor)

    context = {
        'instance': profile_data,
        'portfolio_items': portfolio_items,
        'profile_views': profile_data['views'] if profile_data else 0,
        'portfolio_count': len(portfolio_items),
        # متغيرات مهمة للتمييز بين وضع الأدمن والوضع العادي
        'is_admin_view': True, 
        'target_user': target_user, 
        'role': role,
    }
    
    return render(request, template_name, context)