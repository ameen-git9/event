from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class StaffAdmin(UserAdmin):

    # Only show staff in the admin list
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_staff_user=True)

    list_display = (
        'username', 'staff_id', 'is_staff_user', 'is_active'
    )

    list_filter = ('is_staff_user', 'is_active')

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        
        ("Staff Details", {"fields": ("staff_id", "is_staff_user")}),
        
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser",
                                    "groups", "user_permissions")}),
        
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "password1", "password2",
                "staff_id",
                "is_staff_user",
                "is_staff",
                "is_active",
            ),
        }),
    )


admin.site.register(CustomUser, StaffAdmin)
