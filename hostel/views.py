from django.http import JsonResponse
from django.shortcuts import render
from .models import Hostel
# Create your views here.

def hostel(request):
    # return render(request, 'hostels.html')
    return JsonResponse({ "info ": "Django react course" , "name":"lloyd tony" })