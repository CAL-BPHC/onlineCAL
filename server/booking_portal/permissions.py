from .models import Department, Faculty, LabAssistant, Student


def is_faculty(user):
    if (len(Faculty.objects.filter(email=user.username))) > 0:
        return True
    return False


def is_student(user):
    if (len(Student.objects.filter(email=user.username))) > 0:
        return True
    return False


def is_lab_assistant(user):
    if (len(LabAssistant.objects.filter(email=user.username))) > 0:
        return True
    return False


def is_department(user):
    if (len(Department.objects.filter(email=user.username))) > 0:
        return True
    return False


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
                else "department" if is_department(user) else None
            )
        )
    )
