from django.contrib import admin


class ModePricingRulesAdmin(admin.ModelAdmin):
    list_filter = admin.ModelAdmin.list_filter + ("rule_type", "instrument")
    list_display = admin.ModelAdmin.list_display + ("rule_type", "instrument")

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


class AdditionalPricingRulesAdmin(admin.ModelAdmin):
    list_filter = admin.ModelAdmin.list_filter + ("rule_type", "instrument")
    list_display = admin.ModelAdmin.list_display + ("rule_type", "instrument")

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff
