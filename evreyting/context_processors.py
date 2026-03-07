# evreyting/context_processors.py
from django.db import connection

def user_role(request):
    """Context processor لإرسال رتبة المستخدم ورابط الداش بورد لجميع القوالب"""
    if request.user.is_authenticated:
        with connection.cursor() as cursor:
            cursor.execute("SELECT role FROM evreyting_userprofile WHERE user_id = %s", [request.user.id])
            row = cursor.fetchone()
            role = row[0] if row else 'client'
            
            dashboard_url = None
            if role == 'admin':
                dashboard_url = '/panel/'  
            elif role == 'model':
                dashboard_url = '/dashboard/model/'
            elif role == 'creator':
                dashboard_url = '/dashboard/creator/'
            elif role == 'videographer':
                dashboard_url = '/dashboard/video/'
            elif role == 'voice':
                dashboard_url = '/dashboard/voice/'
            elif role == 'writer':
                dashboard_url = '/dashboard/writer/'
            
            return {'user_role': role, 'dashboard_url': dashboard_url}
    
    return {'user_role': None, 'dashboard_url': None}

# أضف هذه الدالة داخل ملف context_processors.py

def global_banners(request):
    """جلب البنرات النشطة لعرضها في كل الصفحات"""
    from django.db import connection
    
    # لا نريد إرهاق قاعدة البيانات في صفحات الأدمن أو الـ API
    if request.path.startswith('/panel/') or request.path.startswith('/admin/'):
        return {'banners': []}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM evreyting_banner WHERE is_active = TRUE ORDER BY id DESC LIMIT 5")
            banners = dictfetchall(cursor)
        return {'banners': banners}
    except:
        return {'banners': []}

# دالة مساعدة إذا لم تكن موجودة
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]