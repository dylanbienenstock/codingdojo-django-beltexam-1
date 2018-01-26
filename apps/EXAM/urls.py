from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^travels/destination/(?P<trip_id>\d+)$', views.view_trip),
	url(r'^travels/join/(?P<trip_id>\d+)$', views.join_trip),
	url(r'^travels/add/submit$', views.add_trip_submit),
	url(r'^travels/add$', views.add_trip),
	url(r'^travels$', views.view_all_trips),
	url(r'^login$', views.login),
	url(r'^logout$', views.logout),
	url(r'^register$', views.register),
    url(r'^$', views.index),
]
