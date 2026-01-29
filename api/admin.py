from django.contrib import admin
from .models import Blog, Subscriber, ContactMessage, Internship


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'date_created_at']
    search_fields = ['title', 'author']
    list_filter = ['date_created_at']


@admin.register(Subscriber)
class Subscriber(admin.ModelAdmin):
    list_display = ['email', 'created_at']
    search_fields = ['email']


@admin.register(ContactMessage)
class ContactMessage(admin.ModelAdmin):
    list_display = ['name', 'phone', 'subject', 'message']
    list_filter = ['status', 'created_at']
    search_fields = ['subject', 'message']
    readonly_fields = ['created_at']


@admin.register(Internship)
class Internship(admin.ModelAdmin):
    list_display = ['title', 'total_seats', 'is_open']
    list_filter = ['is_open', 'title']
    search_fields = ['title']
