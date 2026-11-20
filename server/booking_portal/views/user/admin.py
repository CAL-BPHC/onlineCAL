import json
from http import HTTPStatus

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import pluralize
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from booking_portal import permissions
from booking_portal.forms.portal import (
    BulkInstrumentAccessForm,
    InstrumentAccessForm,
    StudentSearchForm,
)
from booking_portal.models import Department, Faculty, Instrument, Student

STUDENTS_PER_PAGE = 25


@login_required
def admin_portal(request):
    return redirect("/admin")


@csrf_exempt
@require_POST
def create_student(request):
    api_key = request.headers.get("X-OnlineCIF-API-Key")
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

    supervisor = Faculty.objects.filter(email=supervisor_email).first()
    if not supervisor:
        return JsonResponse(
            {"error": "Supervisor with this email does not exist"},
            status=HTTPStatus.NOT_FOUND,
        )

    raw_password = Student.objects.make_random_password(12)

    if Student.objects.filter(email=email).exists():
        existing = True
        student = Student.objects.get(email=email)
        student.name = name
        student.supervisor = supervisor
        student.password = make_password(raw_password)
        student.save()
    else:
        existing = False
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
            "existing": existing,
        },
        status=HTTPStatus.CREATED,
    )


@csrf_exempt
@require_POST
def create_faculty(request):
    api_key = request.headers.get("X-OnlineCIF-API-Key")
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
    api_key = request.headers.get("X-OnlineCIF-API-Key")
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


@login_required
@user_passes_test(permissions.is_portal_admin)
def instrument_access(request):
    """Every active student and what they may book, to find whose to change.

    Ticking several students assigns or revokes one instrument for all of them.
    """
    if request.method == "POST":
        form = BulkInstrumentAccessForm(request.POST)
        if form.is_valid():
            instrument = form.cleaned_data["instrument"]
            students = form.cleaned_data["students"]
            ticked = f"{len(students)} student{pluralize(len(students))}"
            if form.cleaned_data["action"] == InstrumentAccessForm.ASSIGN:
                instrument.students.add(*students)
                messages.success(request, f"{ticked} can now book {instrument}.")
            else:
                instrument.students.remove(*students)
                messages.success(request, f"{ticked} can no longer book {instrument}.")
        else:
            messages.error(
                request, "Tick at least one student and choose an instrument."
            )
        return redirect(request.get_full_path())

    form = StudentSearchForm(request.GET)
    students = (
        Student.objects.filter(is_active=True)
        .select_related("supervisor")
        .prefetch_related("instruments")
        .order_by("name", "pk")
    )
    if form.is_valid():
        match = Q()
        for term in form.cleaned_data["q"]:
            match |= Q(name__icontains=term) | Q(email__icontains=term)
        students = students.filter(match)
        if form.cleaned_data["instrument"]:
            students = students.filter(instruments=form.cleaned_data["instrument"])

    return render(
        request,
        "booking_portal/portal_forms/instrument_access.html",
        {
            "form": form,
            "page_obj": Paginator(students, STUDENTS_PER_PAGE).get_page(
                request.GET.get("page")
            ),
            "instruments": Instrument.objects.all(),
            "user_type": permissions.get_user_type(request.user),
        },
    )


@login_required
@user_passes_test(permissions.is_portal_admin)
def student_instruments(request, student_id):
    """Assign a student an instrument once they are trained on it, or revoke it."""
    student = get_object_or_404(
        Student.objects.select_related("supervisor"), pk=student_id
    )
    if request.method == "POST":
        form = InstrumentAccessForm(request.POST)
        if form.is_valid():
            instrument = form.cleaned_data["instrument"]
            # one instrument at a time, so two admins changing the same student
            # at once do not undo each other
            if form.cleaned_data["action"] == InstrumentAccessForm.ASSIGN:
                student.instruments.add(instrument)
                messages.success(request, f"{student.name} can now book {instrument}.")
            else:
                student.instruments.remove(instrument)
                messages.success(
                    request, f"{student.name} can no longer book {instrument}."
                )
        else:
            messages.error(request, "Choose an instrument first.")
        return redirect(request.get_full_path())

    return render(
        request,
        "booking_portal/portal_forms/student_instruments.html",
        {
            "student": student,
            "assigned": student.instruments.all(),
            "unassigned": Instrument.objects.exclude(students=student),
            "user_type": permissions.get_user_type(request.user),
        },
    )
