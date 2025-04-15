import json
from http import HTTPStatus

from booking_portal.models import Department, Faculty, Student
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST


@login_required
def admin_portal(request):
    return redirect("/admin")


@csrf_exempt
@require_POST
def create_student(request):
    api_key = request.headers.get("X-OnlineCAL-API-Key")
    if not api_key or api_key != settings.API_KEY:
        return JsonResponse(
            {"error": "Invalid API key"},
            status=HTTPStatus.UNAUTHORIZED,
        )

    try:
        data = json.loads(request.body)
        email = data.get("email")
        name = data.get("name")
        supervisor_email = data.get("supervisor_email")
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=HTTPStatus.BAD_REQUEST,
        )

    if not all([email, name, supervisor_email]):
        return JsonResponse(
            {"error": "Missing required parameters"},
            status=HTTPStatus.BAD_REQUEST,
        )

    if Student.objects.filter(email=email).exists():
        return JsonResponse(
            {"error": "Student with this email already exists"},
            status=HTTPStatus.CONFLICT,
        )

    supervisor = Faculty.objects.filter(email=supervisor_email).first()

    if not supervisor:
        return JsonResponse(
            {"error": "Supervisor with this email does not exist"},
            status=HTTPStatus.NOT_FOUND,
        )

    raw_password = Student.objects.make_random_password(12)

    Student.objects.create(
        email=email,
        name=name,
        supervisor=supervisor,
        password=make_password(raw_password),
    )

    return JsonResponse(
        {
            "success": True,
            "email": email,
            "password": raw_password,
        },
        status=HTTPStatus.CREATED,
    )


@csrf_exempt
@require_POST
def create_faculty(request):
    api_key = request.headers.get("X-OnlineCAL-API-Key")
    if not api_key or api_key != settings.API_KEY:
        return JsonResponse(
            {"error": "Invalid API key"},
            status=HTTPStatus.UNAUTHORIZED,
        )

    try:
        data = json.loads(request.body)
        email = data.get("email")
        name = data.get("name")
        department_email = data.get("department_email")
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=HTTPStatus.BAD_REQUEST,
        )

    if not all([email, name, department_email]):
        return JsonResponse(
            {"error": "Missing required parameters"},
            status=HTTPStatus.BAD_REQUEST,
        )

    if Faculty.objects.filter(email=email).exists():
        return JsonResponse(
            {"error": "Faculty with this email already exists"},
            status=HTTPStatus.CONFLICT,
        )

    department = Department.objects.filter(email=department_email).first()

    if not department:
        return JsonResponse(
            {"error": "Department with this email does not exist"},
            status=HTTPStatus.NOT_FOUND,
        )

    raw_password = Faculty.objects.make_random_password(12)

    Faculty.objects.create(
        email=email,
        name=name,
        department=department,
        password=make_password(raw_password),
    )

    return JsonResponse(
        {
            "success": True,
            "email": email,
            "password": raw_password,
        },
        status=HTTPStatus.CREATED,
    )


@csrf_exempt
@require_GET
def get_faculty(request):
    api_key = request.headers.get("X-OnlineCAL-API-Key")
    if not api_key or api_key != settings.API_KEY:
        return JsonResponse(
            {"error": "Invalid API key"},
            status=HTTPStatus.UNAUTHORIZED,
        )

    faculty_emails = list(Faculty.objects.values_list("email", flat=True))
    if not faculty_emails:
        return JsonResponse(
            {"error": "No faculties found"},
            status=HTTPStatus.NOT_FOUND,
        )

    return JsonResponse(
        {
            "success": True,
            "faculty": faculty_emails,
        },
        status=HTTPStatus.OK,
    )
