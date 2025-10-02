from django.shortcuts import render
from kimi_backend.blockchainClient import w3

# Create your views here.
def index(request):
    return render(request, 'hashPool/index.html')