from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # ===== الصفحات الرئيسية =====
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),

    
    # ===== قوائم الخدمات =====
    path('models/', views.model_list, name='model_list'),
    path('content-creators/', views.content_creator_list, name='content_creator_list'),
    path('video-production/', views.video_production_list, name='video_production_list'),
    path('voice-artists/', views.voice_artist_list, name='voice_artist_list'),
    path('content-writing/', views.content_writing_list, name='content_writing_list'),
    
    # ===== الملفات الشخصية =====
    path('provider/<int:user_id>/', views.provider_profile, name='provider_profile'),
    path('my-portal/', views.provider_portal, name='provider_portal'),
    path('my-portal/delete/<int:item_id>/', views.delete_portfolio_item, name='delete_portfolio_item'),
    path('request-service/', views.request_service, name='request_service'),
    
    # ===== المحادثات =====
    path('my-chats/', views.my_chats, name='my_chats'),
    path('chat/start/<int:provider_id>/', views.start_chat, name='start_chat'),
    path('chat/room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('chat/send/', views.send_message, name='send_message'),
    path('send-message/', views.send_message, name='send_message_alt'),
    
    # ===== لوحات تحكم مقدمي الخدمات =====
    path('dashboard/model/', views.model_dashboard, name='model_dashboard'),
    path('dashboard/model/profile/', views.model_profile_edit, name='model_profile_edit'),
    path('dashboard/model/portfolio/', views.model_portfolio, name='model_portfolio'),
    path('dashboard/creator/', views.creator_dashboard, name='creator_dashboard'),
    path('dashboard/creator/profile/', views.creator_profile_edit, name='creator_profile_edit'),
    path('dashboard/creator/portfolio/', views.creator_portfolio, name='creator_portfolio'),
    path('dashboard/video/', views.video_dashboard, name='video_dashboard'),
    path('dashboard/voice/', views.voice_dashboard, name='voice_dashboard'),
    path('dashboard/voice/profile/', views.voice_profile_edit, name='voice_profile_edit'),
    path('dashboard/voice/portfolio/', views.voice_portfolio, name='voice_portfolio'),
    path('dashboard/writer/', views.writer_dashboard, name='writer_dashboard'),

    # ===== لوحة تحكم الأدمن (مسار panel/) =====
    path('panel/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/users/', views.admin_users, name='admin_users'),
    path('panel/users/edit/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('panel/users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('panel/users/toggle/<int:user_id>/', views.admin_toggle_user, name='admin_toggle_user'),
    path('panel/messages/', views.admin_messages, name='admin_messages'),
    path('panel/user/<int:user_id>/', views.admin_user_panel, name='admin_user_panel'),
    path('panel/portfolio/', views.admin_portfolio, name='admin_portfolio'),
    path('panel/portfolio/delete/<int:item_id>/', views.admin_delete_portfolio, name='admin_delete_portfolio'),
    path('panel/open/<int:user_id>/', views.admin_open_panel, name='admin_open_panel'),
    path('panel/close/', views.admin_close_panel, name='admin_close_panel'),

    
    # === روابط الطلبات والمحادثات للأدمن ===
    path('panel/requests/', views.admin_requests, name='admin_requests'),
    path('panel/chat/<int:room_id>/', views.admin_chat_view, name='admin_chat_view'),
    path('panel/chat/send/', views.admin_send_message, name='admin_send_message'),
    
    # === API ===
    path('get-messages/<int:room_id>/', views.get_messages_api, name='get_messages_api'),

    # === إدارة البنرات ===
    path('panel/banners/', views.admin_banners, name='admin_banners'),
    path('panel/banners/toggle/<int:banner_id>/', views.admin_toggle_banner, name='admin_toggle_banner'),
    path('panel/banners/delete/<int:banner_id>/', views.admin_delete_banner, name='admin_delete_banner'),
]