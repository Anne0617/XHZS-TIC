from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Branch, User, OperationLog


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'contact_phone', 'is_active', 'sort_order']
    list_editable = ['is_active', 'sort_order']
    search_fields = ['name', 'code']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'get_full_name', 'role', 'branch', 'phone', 'is_active', 'is_locked']
    list_filter = ['role', 'branch', 'is_active', 'is_locked']
    search_fields = ['username', 'first_name', 'last_name', 'phone']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('角色信息', {'fields': ('role', 'branch', 'phone', 'department', 'is_locked')}),
        ('权限细分', {'fields': ('can_manage_questions', 'can_manage_tasks', 'can_view_data', 'can_export_data', 'can_manage_employees')}),
    )


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'detail', 'ip_address', 'created_at']
    list_filter = ['action', 'created_at']
    readonly_fields = ['user', 'action', 'detail', 'ip_address', 'created_at']
    search_fields = ['user__username', 'action', 'detail']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
