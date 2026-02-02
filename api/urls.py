from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from django.urls import path
from .import views

urlpatterns = [
    path('', views.PravidhiView),
    path('subscribe/', views.subscribe),
    path('blogs/', views.blog_list),
    path('blogs/<int:pk>/', views.blog_detail),
    path('contactmessage/', views.create_contact),
    path('internship/', views.internship_list),
    path('internship/<int:pk>/', views.internship_detail),
    path('internship/application/', views.create_internship_application),
    path('internship/setup-password/', views.setup_password, name='setup_password'),
    # for token(refresh and acess)
    path('auth/login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('dashboard/my-application/', views.my_application_status,
         name='my_application_status'),
    path('dashboard/available/', views.get_available_internship,
         name='available_internship'),

    path('intern/tasks/', views.intern_task_list),
    path('intern/tasks/<int:pk>/submit/', views.intern_submit_task),
    path('admin/tasks/assign/', views.admin_assign_task),
    path('admin/tasks/<int:pk>/edit/', views.admin_edit_task, name = 'admin_edit_task'),
    path('admin/tasks/<int:pk>/review/', views.admin_review_task, name= 'admin_review_task')
]
