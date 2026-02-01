from django.contrib import admin
from .models import Blog, Subscriber, ContactMessage, Internship, InternshipApplication, Task


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


@admin.register(InternshipApplication)
class InternshipApplicationAdmin(admin.ModelAdmin):
    # This makes the admin list view very useful
    list_display = ('full_name', 'email', 'internship', 'status', 'applied_at')
    list_filter = ('status', 'internship')
    search_fields = ('full_name', 'email')
    list_editable = ('status',) # Allows you to change status directly from the list!

# Register the rest so you can manage them
admin.site.register(Internship)
admin.site.register(Task)


