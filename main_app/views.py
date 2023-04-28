from django.shortcuts import HttpResponse, render, redirect
import requests
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Subway, Stop
import os
import json
from datetime import datetime
from django.utils import timezone
import pytz
import math
# from .static.data import stations

# API_URL = "http://127.0.0.1:5000/"
API_URL = "https://mtapi.herokuapp.com/"
SERVICE_ALERT_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts.json"

station_tz = pytz.timezone('America/New_York')
now = datetime.now(station_tz)
now_in_unix = math.floor(now.timestamp())
# print(now_in_unix)

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

def fav_alerts(request, favorites):
    for fav_subway in favorites:
        subway_id = fav_subway['route_id']
        url = SERVICE_ALERT_URL
        headers = {
            "x-api-key": os.environ.get('MTA_API_KEY'),
            "content-type": "application/json"
        }
        result = requests.get(url, headers=headers)
        if result.status_code == 200:
            data = result.json()
            # print(data)
            alerts = data['entity']
            high_priority_alerts = []
            for alert in alerts:
                for i in range(len(alert['alert']['informed_entity'])):
                    # check if the alert is for the subway line and if it is high priority
                    if 'transit_realtime.mercury_entity_selector' in alert['alert']['informed_entity'][i]:
                        train_line, priority = alert['alert']['informed_entity'][i]['transit_realtime.mercury_entity_selector']['sort_order'].split(':')[1:]
                        priority = int(priority)
                        if train_line == subway_id and priority > 19:
                            # check if alert is active
                            if alert['alert']['active_period'][0]['start'] < now_in_unix:
                                high_priority_alerts.append({
                                    "text": alert['alert']['header_text']['translation'][0]['text'],
                                    "priority": priority,
                                })
            #remove duplicates
            high_priority_alerts = list({alert['text']: alert for alert in high_priority_alerts}.values())
            # sort by priority
            high_priority_alerts.sort(key=lambda x: x['priority'], reverse=True)
            # only show the top 3 alerts
            high_priority_alerts = high_priority_alerts[:3]
            fav_subway['alerts'] = high_priority_alerts
    return render(request, 'favorite_subways.html', {
        "subways": favorites,
    })
    

def subway_list(request):
    subways = Subway.objects.filter(user=request.user)
    favorites = []
    # ids = []
    for subway in subways:
        url = API_URL + "by-route/" + subway.route_id
        result = requests.get(url)
        if result.status_code == 200:
            data = result.json()
            stations = data['data']
            sorted_stations = sorted(stations, key=lambda x: x['location'][0], reverse=True)
            fav_subway = {
                "route_id": subway.route_id,
                "stations": sorted_stations,
                "alerts": []
            }
            favorites.append(fav_subway)
            # ids.append(subway.route_id)
    
    return fav_alerts(request, favorites)

def station_list(request):
    stations = Stop.objects.filter(user=request.user)
    favorites = []
    now = datetime.now(station_tz)
    for station in stations:
        url = API_URL + "by-id/" + station.station_id + "?time=" + now.strftime("%H:%M")
        result = requests.get(url)
        if result.status_code == 200:
            data = result.json()
            for stop in data['data']:
                for direction in ['N', 'S']:
                    for departure in stop[direction]:
                        train_time_str = departure['time']
                        train_time = datetime.fromisoformat(train_time_str)
                        time_until_train = (train_time - now).total_seconds()/60
                        departure['time'] = train_time.astimezone(station_tz).strftime("%I:%M %p")
                        departure['time_until_train'] = time_until_train.__trunc__()
            fav_station = {
                "station_id": station.station_id,
                "station_data": data['data'][0],
            }
            favorites.append(fav_station)
            # print(favorites)
    return render(request, 'favorite_stations.html', {
        "now": now,
        "stations": favorites,
        })

def subway_alerts(request, subway_id, sorted_stations, fav_subway):
    url = SERVICE_ALERT_URL
    headers = {
        "x-api-key": os.environ.get('MTA_API_KEY'),
        "content-type": "application/json"
    }
    result = requests.get(url, headers=headers)
    if result.status_code == 200:
        data = result.json()
        # print(data)
        alerts = data['entity']
        high_priority_alerts = []
        for alert in alerts:
            for i in range(len(alert['alert']['informed_entity'])):
                # check if the alert is for the subway line and if it is high priority
                if 'transit_realtime.mercury_entity_selector' in alert['alert']['informed_entity'][i]:
                    train_line, priority = alert['alert']['informed_entity'][i]['transit_realtime.mercury_entity_selector']['sort_order'].split(':')[1:]
                    priority = int(priority)
                    if train_line == subway_id and priority > 19:
                        # check if alert is active
                        if alert['alert']['active_period'][0]['start'] < now_in_unix:
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
            "fav_subway": fav_subway,
        })
    return HttpResponse('Something went wrong')

def subway_detail(request, subway_id):
    if Subway.objects.filter(user=request.user.id, route_id=subway_id).exists():
        fav_subway = True
    else:
        fav_subway = False
    url = f"{API_URL}by-route/{subway_id}"
    result = requests.get(url)
    if result.status_code == 200:
        data = result.json()
        stations = data['data']
        sorted_stations = sorted(stations, key=lambda x: x['location'][0], reverse=True)
        # call the subway_alerts function to get alerts
        return subway_alerts(request, subway_id, sorted_stations, fav_subway)
    return HttpResponse('Something went wrong')

def station_detail(request, station_id):
    # check if station is in favorites
    if Stop.objects.filter(user=request.user.id, station_id=station_id).exists():
        fav_station = True
    else:
        fav_station = False
    # add time query to prevent caching
    now = datetime.now(station_tz)
    url = f"{API_URL}by-id/{station_id}?time={now}"
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
            "now": now,
            "station_id": station_id,
            "station_data": data['data'][0],
            "fav_station": fav_station,
        })
    return HttpResponse('Something went wrong')

@login_required
def add_subway(request, subway_id):
    subway = Subway.objects.create(
        user=request.user,
        route_id=subway_id,
    )
    return redirect('subway_detail', subway_id=subway_id)

@login_required
def add_station(request, station_id):
    station = Stop.objects.create(
        user=request.user,
        station_id=station_id,
    )
    return redirect('station_detail', station_id=station_id)

@login_required
def remove_subway(request, subway_id):
    subway = Subway.objects.filter(
        user=request.user,
        route_id=subway_id,
    ).delete()
    return redirect('subway_detail', subway_id=subway_id)

@login_required
def remove_station(request, station_id):
    station = Stop.objects.filter(
        user=request.user,
        station_id=station_id,
    ).delete()
    return redirect('station_detail', station_id=station_id)

def test(request):
    pass

