from django.shortcuts import render


def index(request):
    return render(request, "onlineCAL/home.html")
