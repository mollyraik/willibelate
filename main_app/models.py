from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Route(models.Model):
    id = models.BigAutoField(primary_key=True)
    route_id = models.CharField(max_length=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timeAdded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.route_id
    

class Station(models.Model):
    id = models.BigAutoField(primary_key=True)
    station_id = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timeAdded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
