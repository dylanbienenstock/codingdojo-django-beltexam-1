# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, HttpResponse
from .models import User, Trip

default_page = "/travels"

def index(request):
	if "user_id" in request.session:
		return redirect(default_page)

	return render(request, "index.html")

def register(request):
	if request.method == "POST":
		response = User.objects.register(request.POST)

		if not response["success"]:
			return render(request, "index.html", response)

		request.session["user_id"] = response["user_id"]
		request.session["user_name"] = response["user_name"]

	return redirect("/")

def login(request):
	if request.method == "POST":
		response = User.objects.login(request.POST)

		if not response["success"]:
			return render(request, "index.html", response)

		request.session["user_id"] = response["user_id"]
		request.session["user_name"] = response["user_name"]

	return redirect("/")

def logout(request):
	request.session.flush()

	return redirect("/")

def add_trip(request):
	if not "user_id" in request.session:
		return redirect("/")

	context = {
		"user_name": request.session["user_name"]
	}

	return render(request, "new_trip.html", context)

def add_trip_submit(request):
	if "user_id" in request.session:
		response = Trip.objects.addTrip(request.POST, request.session["user_id"])
		response["user_name"] = request.session["user_name"]

		if not response["success"]:
			return render(request, "new_trip.html", response)

	return redirect("/")

def view_all_trips(request):
	if not "user_id" in request.session:
		return redirect("/")

	user = User.objects.filter(id=request.session["user_id"]).first()
	your_trips = user.trips.all()

	if user:
		context = {
			"user_name": request.session["user_name"],
			"your_trips": user.trips.all(),
			"other_trips": Trip.objects.difference(your_trips)
		}

		return render(request, "view_all_trips.html", context)

	return redirect("/")

def view_trip(request, trip_id):
	if not "user_id" in request.session:
		return redirect("/")

	trip = Trip.objects.filter(id=trip_id).first()

	if trip:
		context = {
			"user_name": request.session["user_name"],
			"trip": trip,
			"other_users": trip.members.exclude(id=trip.original_planner.id)
		}

		return render(request, "view_trip.html", context)

	return redirect("/")

def join_trip(request, trip_id):
	if not "user_id" in request.session:
		return redirect("/")

	user = User.objects.filter(id=request.session["user_id"]).first()
	trip = Trip.objects.filter(id=trip_id).first()

	if user and trip:
		user.trips.add(trip)

	return redirect("/")