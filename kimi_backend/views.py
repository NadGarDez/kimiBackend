from django.shortcuts import render

def projectIndex(request):
    return render(request, 'index.html')