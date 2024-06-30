from django.contrib import admin
from rangefilter.filter import DateRangeFilter


class RequestAdmin(admin.ModelAdmin):
    list_filter = (
        ("slot__date", DateRangeFilter),
        "lab_assistant",
        "status",
        "instrument",
    )
    list_display = admin.ModelAdmin.list_display + (
        "student",
        "faculty",
        "lab_assistant",
        "status",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class FacultyRequestAdmin(admin.ModelAdmin):
    list_filter = (
        ("slot__date", DateRangeFilter),
        "lab_assistant",
        "status",
        "instrument",
    )
    list_display = admin.ModelAdmin.list_display + (
        "faculty",
        "lab_assistant",
        "status",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
