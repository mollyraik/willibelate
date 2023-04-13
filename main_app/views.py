from django.shortcuts import HttpResponse, render
import requests
import os
import json

# Create your views here.
def home(request):
    url = "http://127.0.0.1:5000/routes"
    # header = {
    # "MTA_KEY": os.environ['MTA_API_KEY'],
    # "content-type": "application/json"
    # }
    result = requests.get(url)
    if result.status_code == 200:
        data = result.json()
        return render(request, 'home.html', {
            "data": data,
        })
    return HttpResponse('Something went wrong')