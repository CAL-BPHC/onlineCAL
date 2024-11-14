from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def admin_portal(request):
    return redirect("/admin")
