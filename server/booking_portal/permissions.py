from .models import CustomUser, Department, Faculty, LabAssistant, Student


def is_faculty(user):
    return Faculty.objects.filter(email=user.username).exists()


def is_student(user):
    return Student.objects.filter(email=user.username).exists()


def is_lab_assistant(user):
    return LabAssistant.objects.filter(email=user.username).exists()


def is_department(user):
    return Department.objects.filter(email=user.username).exists()


def is_portal_admin(user):
    return user.is_superuser or user.role == CustomUser.Role.PORTAL_ADMIN


def get_user_type(user):
    return (
        "faculty"
        if is_faculty(user)
        else (
            "assistant"
            if is_lab_assistant(user)
            else (
                "student"
                if is_student(user)
                else "department"
                if is_department(user)
                else None
            )
        )
    )
