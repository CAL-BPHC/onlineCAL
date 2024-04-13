from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

from ..models import EmailModel


@login_required
def email(request):
    # returns emails of all users.
    emails = EmailModel.objects.all()
    context = {
        'emails': emails,
    }
    return render(request, 'email.html', context=context)
