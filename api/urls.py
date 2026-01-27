from django.urls import path
from .import views

urlpatterns = [
    path('',views.PravidhiView),
    path('subscribe/', views.subscribe),
    path('blogs/', views.blog_list),
    path('blogs/<int:pk>/', views.blog_detail),
    path('contactmessage/', views.create_contact)
]