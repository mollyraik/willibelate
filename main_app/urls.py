from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('test/', views.test, name='test'),
    path('accounts/signup/', views.signup, name='signup'),
    path('line/favorites/', views.subway_list, name='favorite_subways'),
    path('station/favorites/', views.station_list, name='favorite_stations'),
    path('line/<str:subway_id>/', views.subway_detail, name='subway_detail'),
    path('station/<str:station_id>/', views.station_detail, name='station_detail'),
]