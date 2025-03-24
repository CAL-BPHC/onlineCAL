import json
from http import HTTPStatus

from booking_portal.models import Faculty, Student
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


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
