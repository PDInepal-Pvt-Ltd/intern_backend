from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # General / Public
    path('', views.PravidhiView),
    path('subscribe/', views.subscribe),
    path('blogs/', views.blog_list),
    path('blogs/<int:pk>/', views.blog_detail),
    path('contactmessage/', views.create_contact),

    # Internship Public/Applicant Flow
    path('internship/', views.internship_list),
    path('internship/<int:pk>/', views.internship_detail),
    path('internship/application/', views.create_internship_application),
    path('internship/setup-password/', views.setup_password, name='setup_password'),

    # Authentication
    path('auth/login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Intern Dashboard (For the logged-in Intern)
    path('dashboard/my-application/', views.my_application_status, name='my_application_status'),
    path('dashboard/available-internship/', views.get_available_internship, name='available_internship'),
    path('intern/tasks/', views.intern_task_list),
    path('intern/tasks/<int:pk>/submit/', views.intern_submit_task),

    # Management Portal (For the Admin/Staff Frontend)
    # Changed 'admin' to 'management' to avoid Django conflicts
    path('management/tasks/assign/', views.admin_assign_task, name='admin_assign_task'),
    path('management/tasks/view/', views.admin_view_tasks, name='admin_view_tasks'),
    path('management/tasks/<int:pk>/edit/', views.admin_edit_task, name='admin_edit_task'),
    path('management/tasks/<int:pk>/review/', views.admin_review_task, name='admin_review_task'),
    
    # User and Application Management (The ones we built today)
    path('management/dashboard-stats/', views.admin_dashboard_stats, name='admin_stats'),
    path('management/users/', views.admin_user_manager, name='admin_user_management'),
    path('management/contacts/', views.admin_contact_list, name='admin_contact_list'),
    path('management/contacts/<int:pk>/delete/', views.admin_contact_delete, name='admin_contact_delete'),
    path('management/applications/', views.admin_application_list, name='admin_application_list'),
    path('management/applications/<int:pk>/status/', views.admin_update_application_status, name='admin_update_application_status'),
    path('management/newsletter/broadcast/', views.admin_broadcast_newsletter, name='broadcast_news'),
    path('management/users/create-admin/', views.admin_create_staff, name='create_admin')
]