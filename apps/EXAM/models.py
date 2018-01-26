# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import re, md5, os, binascii
from datetime import date

class UserManager(models.Manager):
	def length_within_range(self, val, min, max):
		return len(val) >= min and len(val) <= max

	def register(self, POST):
		response = {
			"response_type": "registration",
			"success": True,
			"errors": [],
			"user_id": None,
			"user_name": None
		}

		# Ensure complete form submission

		if (not "real_name" in POST
		or not "user_name" in POST
		or not "password" in POST
		or not "confirm_password" in POST):
			response["success"] = False
			response["errors"] += ["Incomplete form submission."]

			return response

		# Strip whitespace and set email to lowercase
		# (new variables because QueryDict is immutable)

		real_name = POST["real_name"].rstrip()
		user_name = POST["user_name"].rstrip().lower()

		# Validate name

		if not self.length_within_range(real_name, 3, 75):
			response["success"] = False
			response["errors"] += ["Real name must be within 3-75 characters."]

		if not self.length_within_range(user_name, 3, 75):
			response["success"] = False
			response["errors"] += ["Username must be within 3-75 characters."]

		if self.filter(user_name=user_name).exists():
			response["success"] = False
			response["errors"] += ["The specified username is already in use."]

		# Validate password

		if not self.length_within_range(POST["password"], 8, 255):
			response["success"] = False
			response["errors"] += ["Password must be within 8-255 characters."]

		if not POST["password"] == POST["confirm_password"]:
			response["success"] = False
			response["errors"] += ["Passwords must match."]

		# Create User

		if response["success"]:
			password_salt = binascii.b2a_hex(os.urandom(15))
			password_hash = md5.new(POST["password"] + password_salt).hexdigest()

			user = User.objects.create(
				real_name = real_name,
				user_name = user_name,
				password_hash = password_hash,
				password_salt = password_salt
			)

			response["user_id"] = user.id
			response["user_name"] = user.real_name


		return response

	def login(self, POST):
		response = {
			"response_type": "login",
			"success": True,
			"errors": [],
			"user_id": None,
			"user_name": None
		}

		if (not "user_name" in POST
		or not "password" in POST):
			response["success"] = False
			response["errors"] += ["Incomplete form submission."]

			return response

		user_name = POST["user_name"].rstrip().lower()
		user = User.objects.filter(user_name=user_name).first()

		if not user:
			response["success"] = False
			response["errors"] += ["There is no account with the specified username."]

			return response

		password_hash = md5.new(POST["password"] + user.password_salt).hexdigest()

		if not password_hash == user.password_hash:
			response["success"] = False
			response["errors"] += ["Incorrect password."]

		response["user_id"] = user.id
		response["user_name"] = user.real_name

		return response

class User(models.Model):
	real_name = models.CharField(max_length=75)
	user_name = models.CharField(max_length=75)
	password_hash = models.CharField(max_length=32)
	password_salt = models.CharField(max_length=32)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	objects = UserManager()

class TripManager(models.Manager):
	def string_to_date(self, date_string):
		date_regex = r"^(\d{1,2})\/(\d{1,2})\/(\d{4})$"

		if re.match(date_regex, date_string):
			groups = re.search(date_regex, date_string).groups()
			today = date.today()

			month = int(groups[0])
			day = int(groups[1])
			year = int(groups[2])

			try:
				return date(year, month, day)
			except:
				return None

		return None


	def addTrip(self, POST, user_id):		
		response = {
			"response_type": "add_trip",
			"success": True,
			"errors": []
		}

		# Ensure complete form submission

		if (not "destination" in POST
		or not "description" in POST
		or not "date_from" in POST
		or not "date_to" in POST):
			response["success"] = False
			response["errors"] += ["Incomplete form submission."]

			return response


		destination = POST["destination"].rstrip()
		description = POST["description"].rstrip()
		date_from = self.string_to_date(POST["date_from"])
		date_to = self.string_to_date(POST["date_to"])

		if not User.objects.length_within_range(destination, 3, 75):
			response["success"] = False
			response["errors"] += ["Destination must be within 3-75 characters."]

		if not User.objects.length_within_range(description, 3, 75):
			response["success"] = False
			response["errors"] += ["Destination must be within 3-75 characters."]

		if not date_from or not date_to:
			response["success"] = False
			response["errors"] += ["Travel dates must be valid."]
		else:
			if date_from < date.today() or date_to < date.today():
				response["success"] = False
				response["errors"] += ["Travel dates must be in the future."]

			if date_from > date_to:
				response["success"] = False
				response["errors"] += ["From date must be before to date."]

		if response["success"]:
			user = User.objects.filter(id=user_id).first()

			if not user:
				response["success"] = False
				response["errors"] += ["No user with that ID. HACKER BAD >:("]
			else:
				trip = Trip.objects.create(
					destination=destination,
					description=description,
					date_to=date_to,
					date_from=date_from,
					original_planner=user,
				)

				trip.members.add(user)

		return response


class Trip(models.Model):
	destination = models.CharField(max_length=75)
	description = models.CharField(max_length=75)
	date_from = models.DateField()
	date_to = models.DateField()
	original_planner = models.ForeignKey(User)
	members = models.ManyToManyField(User, related_name="trips")

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	objects = TripManager()