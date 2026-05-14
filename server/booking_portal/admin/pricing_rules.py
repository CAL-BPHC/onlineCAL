from booking_portal.models import CustomUser
from django.contrib import admin


class ModePricingRulesAdmin(admin.ModelAdmin):
    list_filter = admin.ModelAdmin.list_filter + ("rule_type", "instrument")
    list_display = admin.ModelAdmin.list_display + ("rule_type", "instrument")

    def has_add_permission(self, request):
        return (
            request.user.role == CustomUser.Role.PORTAL_ADMIN
            or request.user.role == CustomUser.Role.LAB_ASSISTANT
            or request.user.is_superuser
        )

    def has_change_permission(self, request, obj=None):
        return (
            request.user.role == CustomUser.Role.PORTAL_ADMIN
            or request.user.role == CustomUser.Role.LAB_ASSISTANT
            or request.user.is_superuser
        )

    def has_delete_permission(self, request, obj=None):
        return (
            request.user.role == CustomUser.Role.PORTAL_ADMIN
            or request.user.role == CustomUser.Role.LAB_ASSISTANT
            or request.user.is_superuser
        )


class AdditionalPricingRulesAdmin(admin.ModelAdmin):
    list_filter = admin.ModelAdmin.list_filter + ("rule_type", "instrument")
    list_display = admin.ModelAdmin.list_display + ("rule_type", "instrument")

    def has_add_permission(self, request):
        return (
            request.user.role == CustomUser.Role.PORTAL_ADMIN
            or request.user.role == CustomUser.Role.LAB_ASSISTANT
            or request.user.is_superuser
        )

    def has_change_permission(self, request, obj=None):
        return (
            request.user.role == CustomUser.Role.PORTAL_ADMIN
            or request.user.role == CustomUser.Role.LAB_ASSISTANT
            or request.user.is_superuser
        )

    def has_delete_permission(self, request, obj=None):
        return (
            request.user.role == CustomUser.Role.PORTAL_ADMIN
            or request.user.role == CustomUser.Role.LAB_ASSISTANT
            or request.user.is_superuser
        )
