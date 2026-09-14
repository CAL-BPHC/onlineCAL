from .models import Department, Faculty, LabAssistant, Student


def is_faculty(user):
    return len(Faculty.objects.filter(email=user.username)) > 0


def is_student(user):
    return len(Student.objects.filter(email=user.username)) > 0


def is_lab_assistant(user):
    return len(LabAssistant.objects.filter(email=user.username)) > 0


def is_department(user):
    return len(Department.objects.filter(email=user.username)) > 0


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
