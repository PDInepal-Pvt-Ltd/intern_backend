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
        # checking if user is logged in
        is_authenticated = bool(request.user and request.user.is_authenticated)
        # user has the application attrubute
        has_application = hasattr(request.user, 'application')
        # making sure they are not staff
        not_staff = not request.user.is_staff
        return is_authenticated and has_application and not_staff