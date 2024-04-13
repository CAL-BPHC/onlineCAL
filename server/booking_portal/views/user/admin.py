from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def admin_portal(request):
    return redirect('/admin')
