from rest_framework import permissions

class IsStaffOrAdmin(permissions.BasePermission):
    # only allows access to staff and superuser
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )
    
class IsIntern(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.applications.exists() and 
            not request.user.is_staff
        )
    
class IsOwner(permissions.BasePermission):
    # to make a user only accesses his only specific data records
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True

        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'assigned_to'):
            return obj.assigned_to == request.user
        return False
    
class IsAcceptedIntern(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        return request.user.applications.filter(status='accepted').exists()