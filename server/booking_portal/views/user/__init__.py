from .admin import admin_portal, create_faculty, create_student, get_faculty
from .department import department_accept, department_portal, department_reject
from .faculty import (
    faculty_portal,
    faculty_request_accept,
    faculty_request_portal,
    faculty_request_reject,
)
from .lab_assistant import (
    lab_assistant_accept,
    lab_assistant_faculty_portal,
    lab_assistant_portal,
    lab_assistant_reject,
)
from .profile import user_profile
from .student import book_machine, student_portal
from .user import about_us, announcements, change_password, guidelines
