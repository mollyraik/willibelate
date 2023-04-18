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
SERVICE_ALERT_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts.json"

station_tz = pytz.timezone('America/New_York')
now = datetime.now(station_tz)
now_in_unix = math.floor(now.timestamp())
print(now_in_unix)

# Create your views here.
def home(request):
    return render(request, 'home.html')
    


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

def subway_alerts(request, subway_id, sorted_stations):
    url = SERVICE_ALERT_URL
    headers = {
        "x-api-key": os.environ.get('MTA_API_KEY'),
        "content-type": "application/json"
    }
    result = requests.get(url, headers=headers)
    if result.status_code == 200:
        data = result.json()
        # print(result)
        alerts = data['entity']
        high_priority_alerts = []
        for alert in alerts:
            for i in range(len(alert['alert']['informed_entity'])):
                # check if the alert is for the subway line and if it is high priority
                if 'transit_realtime.mercury_entity_selector' in alert['alert']['informed_entity'][i]:
                    train_line, priority = alert['alert']['informed_entity'][i]['transit_realtime.mercury_entity_selector']['sort_order'].split(':')[1:]
                    priority = int(priority)
                    if train_line == subway_id and priority > 19:
                        high_priority_alerts.append({
                            "text": alert['alert']['header_text']['translation'][0]['text'],
                            "priority": priority,
                        })
        # remove duplicates
        high_priority_alerts = list({alert['text']: alert for alert in high_priority_alerts}.values())
        # sort by priority
        high_priority_alerts.sort(key=lambda x: x['priority'], reverse=True)
        # only show the top 3 alerts
        high_priority_alerts = high_priority_alerts[:3]
        return render(request, 'subway_detail.html', {
            "subway": subway_id,
            "alerts": high_priority_alerts,
            "stations": sorted_stations,
        })
    return HttpResponse('Something went wrong')

def subway_detail(request, subway_id):
    url = f"{API_URL}by-route/{subway_id}"
    result = requests.get(url)
    if result.status_code == 200:
        data = result.json()
        stations = data['data']
        sorted_stations = sorted(stations, key=lambda x: x['location'][0], reverse=True)
        # call the subway_alerts function to get alerts
        return subway_alerts(request, subway_id, sorted_stations)
    return HttpResponse('Something went wrong')

def station_detail(request, station_id):
    # add time query to prevent caching
    url = f"{API_URL}by-id/{station_id}?time={now_in_unix}"
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

# def test(request):
#     url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts.json"
#     headers = {
#         "x-api-key": "Yiwi9kjBbi9VLTh4C6fRI4TBYF1ijJoJ1mzDats9",
#         "content-type": "application/json"
#         }
#     result = requests.get(url, headers=headers)
#     if result.status_code == 200:
#         data = result.json()
#         new_data = json.dumps(data, indent=4, sort_keys=True)
#         for i in range(len(data['entity'])):
#             if ":32" in data['entity'][i]['alert']['informed_entity'][0]['transit_realtime.mercury_entity_selector']['sort_order'] and '[1]' in data['entity'][i]['alert']['header_text']['translation'][0]['text']:
#                 print(data['entity'][i]['alert']['header_text']['translation'][0]['text'])
#         return HttpResponse(new_data)
#     return HttpResponse('Something went wrong')

