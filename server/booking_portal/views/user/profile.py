from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from booking_portal.models.user import Department, Faculty, LabAssistant, Student


@login_required
def user_profile(request):
    faculty_instance = Faculty.objects.filter(id=request.user.id).first()
    student_instance = Student.objects.filter(id=request.user.id).first()
    lab_instance = LabAssistant.objects.filter(id=request.user.id).first()
    department_instance = Department.objects.filter(id=request.user.id).first()

    if faculty_instance:
        user_type = "faculty"
        instance = faculty_instance
    elif student_instance:
        user_type = "student"
        instance = student_instance
    elif lab_instance:
        user_type = "assistant"
        instance = lab_instance
    elif department_instance:
        user_type = "department"
        instance = department_instance
    else:
        user_type = "none"
        instance = None
    return render(
        request, "profile.html", {"user_type": user_type, "instance": instance}
    )
