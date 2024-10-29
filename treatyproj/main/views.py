from django.shortcuts import render


def index(request):
    return render(request, 'main/index.html')

def catalog(request):
    return render(request, 'main/catalog.html')

def profile(request):
    return render(request, 'main/profile.html')

def help(request):
    return render(request, 'main/help.html')