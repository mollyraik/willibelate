from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Route(models.Model):
    route_id = models.CharField(max_length=2, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.route_id
    

class Station(models.Model):
    station_id = models.CharField(max_length=10, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
