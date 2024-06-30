from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from ..models import Department, Faculty


class ContentTypeListFilter(admin.SimpleListFilter):
    title = "content type"
    parameter_name = "content_type"

    def lookups(self, request, model_admin):
        return (
            (ContentType.objects.get_for_model(Department).id, "Department"),
            (ContentType.objects.get_for_model(Faculty).id, "Faculty"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type_id=self.value())
        return queryset


class BalanceTopUpLogAdmin(admin.ModelAdmin):
    list_filter = (ContentTypeListFilter,)
    list_display = admin.ModelAdmin.list_display + (
        "admin_user",
        "date",
        "top_up_amount",
        "recipient",
        "content_type",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
