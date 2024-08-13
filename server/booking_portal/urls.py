from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("book-machine/<int:instr_id>", views.book_machine, name="book-machine"),
    path("email/", views.email, name="email"),
    path("instrument-list/", views.instrument_list, name="instrument-list"),
    path("view-slots/", views.slot_list, name="slot-list"),
    path("faculty/", views.faculty_portal, name="faculty_portal"),
    path(
        "faculty/requests", views.faculty_request_portal, name="faculty_request_portal"
    ),
    path("lab-assistant/", views.lab_assistant_portal, name="lab_assistant"),
    path(
        "lab-assistant/faculty",
        views.lab_assistant_faculty_portal,
        name="lab_assistant_faculty_portal",
    ),
    path("student/", views.student_portal, name="student"),
    path("department/", views.department_portal, name="department_portal"),
    path(
        "requests_faculty/accept/<int:id>",
        views.faculty_request_accept,
        name="faculty_request_accept",
    ),
    path(
        "requests_faculty/reject/<int:id>",
        views.faculty_request_reject,
        name="faculty_request_reject",
    ),
    path(
        "requests_assistant/accept/<int:id>",
        views.lab_assistant_accept,
        name="lab_assistant_request_accept",
    ),
    path(
        "requests_assistant/reject/<int:id>",
        views.lab_assistant_reject,
        name="lab_assistant_request_reject",
    ),
    path(
        "requests_department/accept/<int:id>",
        views.department_accept,
        name="department_request_accept",
    ),
    path(
        "requests_department/reject/<int:id>",
        views.department_reject,
        name="department_request_reject",
    ),
    path("application/view/<int:id>", views.show_application, name="view-application"),
    path("application/edit/remarks/<int:id>", views.add_remarks, name="add_remarks"),
    path("admin-portal/", views.admin_portal, name="admin_portal"),
    path("about-us/", views.about_us, name="about_us"),
    path("announcements/", views.announcements, name="announcements"),
    path("profile", views.user_profile, name="profile"),
]
