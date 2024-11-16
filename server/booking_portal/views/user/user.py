from booking_portal.models import Announcement
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, "Your password was successfully updated!")
            return redirect("change_password")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "accounts/change_password.html", {"form": form})


def about_us(request):
    return render(request, "about_us.html")


def guidelines(request):
    return render(request, "guidelines.html")


def announcements(request):
    announcements = Announcement.objects.all().order_by("-date")
    context = {
        "announcements": announcements,
    }
    return render(request, "announcements.html", context=context)
