from django.shortcuts import HttpResponse, render, redirect
import requests
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Route, Station
import os
import json
from datetime import datetime
from django.utils import timezone
import pytz
import math

API_URL = "http://127.0.0.1:5000/"

station_tz = pytz.timezone('America/New_York')
now = datetime.now(timezone.utc)

# Create your views here.
def home(request):
    return render(request, 'home.html')
    

def test(request):
    url = "http://web.mta.info/status/serviceStatus.txt"
    headers = {
    "x-api-key": "Yiwi9kjBbi9VLTh4C6fRI4TBYF1ijJoJ1mzDats9",
    "content-type": "application/json"
    }
    result = requests.get(url, headers=headers)
    if result.status_code == 200:
        data = result.json()
        return HttpResponse(result)
    return HttpResponse('Something went wrong')

def signup(request):
    error_message = ''
    # POST request
    if request.method == 'POST':
        # create a user using the UserCreationForm -- this way we can validate the form
        form = UserCreationForm(request.POST)
        # check if the form inputs are valid
        if form.is_valid():
        # if valid; save new user to the database
            user = form.save()
            # login the new user
            login(request, user)
            # redirect to the cats index page
            return redirect('home')
        else:
        # else: generate an error message -- 
            error_message = 'Invalid sign up - please try again'

    # GET requests
        # send an empty form to the client
    form = UserCreationForm()
    return render(request, 'registration/signup.html', { 
        'form': form, 
        'error': error_message
    })

def subway_list(request):
    subways = Route.objects.filter(user=request.user)
    return render(request, 'favorite_subways.html')

def station_list(request):
    stations = Station.objects.filter(user=request.user)
    return render(request, 'favorite_stations.html')

def subway_detail(request, subway_id):
    url = f"{API_URL}by-route/{subway_id}"
    result = requests.get(url)
    if result.status_code == 200:
        data = result.json()
        stations = data['data']
        sorted_stations = sorted(stations, key=lambda x: x['location'][0], reverse=True)
        return render(request, 'subway_detail.html', {
            "subway": subway_id,
            "stations": sorted_stations,
        })
    return HttpResponse('Something went wrong')

def station_detail(request, station_id):
    url = f"{API_URL}by-id/{station_id}"
    result = requests.get(url)
    if result.status_code == 200:
        data = result.json()
        for station in data['data']:
            for direction in ['N', 'S']:
                for departure in station[direction]:
                    train_time_str = departure['time']
                    train_time = datetime.fromisoformat(train_time_str)
                    time_until_train = (train_time - now).total_seconds()/60
                    departure['time'] = train_time.astimezone(station_tz).strftime("%I:%M %p")
                    departure['time_until_train'] = time_until_train.__trunc__()
                    

        return render(request, 'station_detail.html', {
            "station_id": station_id,
            "station_data": data['data'][0],
        })
    return HttpResponse('Something went wrong')

