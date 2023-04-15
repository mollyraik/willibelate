from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Route(models.Model):
    route_id = models.CharField(max_length=2, primary_key=True)
    agency_id = models.CharField(max_length=10, default='MTA NYCT')
    route_short_name = models.CharField(max_length=2)
    route_long_name = models.CharField(max_length=50)
    route_desc = models.TextField()
    route_type = models.IntegerField(default=1)
    route_url = models.CharField(max_length=50)
    route_color = models.CharField(max_length=6, null=True)
    route_text_color = models.CharField(max_length=6, null=True)
    user = models.ManyToManyField(User)

    def __str__(self):
        return self.route_id

class Station(models.Model):
    stop_id = models.CharField(max_length=4)
    name = models.CharField(max_length=50)
    lat = models.FloatField()
    lon = models.FloatField()
    parent_id = models.CharField(max_length=4)
    json_id = models.CharField(max_length=4, null=True)
    user = models.ManyToManyField(User)

    def __str__(self):
        return self.name
    
