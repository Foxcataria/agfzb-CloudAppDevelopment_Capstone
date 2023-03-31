from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from .models import CarModel
import logging
import json
import os
from dotenv import load_dotenv

# Get an instance of a logger
logger = logging.getLogger(__name__)

load_dotenv()

# Create your views here.

# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Check for POST request
    if request.method == "POST":
        # Extract the username and password from the POST request
        username = request.POST['username']
        password = request.POST['psw']
        # Check if there is an already registered user with the given credentials
        user = authenticate(username=username, password=password)
        if user is not None:
            # Log the user in and redirect to the applications index page
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # Return to login page
            return render(request, 'djangoapp/login.html', context)
    else:
        # Return to login page
        return render(request, 'djangoapp/login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    context = {}
    # Logout the current user
    logout(request)
    # Redirect to the applications index page
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If GET request is recieved then show the user the applications registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Extract key elements of the current registering user from the POST request
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        # Check if a user with the same credentials already exists. Otherwise create
        # the new user, add the user to the applications database and login the user
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    get_dealership_url = os.environ['get_dealership_url']

    context = {}
    if request.method == "GET":
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(get_dealership_url)
        # Concat all dealer's short name
        context["dealership_list"] = dealerships
        # Return a list of dealer short name
        
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    get_dealership_url = os.environ['get_dealership_url']
    get_review_url = os.environ['get_review_url']

    context = {}
    if request.method == "GET":
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(get_dealership_url)
        current_dealer_name = ""
        for dealer in dealerships:
            if dealer.id == dealer_id:
                current_dealer_name = dealer.full_name
        dealer_reviews = get_dealer_reviews_from_cf(get_review_url, dealer_id)
        context["dealer_reviews_list"] = dealer_reviews
        context["current_dealer_name"] = current_dealer_name
        context["current_dealer_id"] = dealer_id
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    get_dealership_url = os.environ['get_dealership_url']
    post_review_url = os.environ['post_review_url']

    if request.method == "GET":
        context = {}
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(get_dealership_url)
        current_dealer_name = ""
        for dealer in dealerships:
            if dealer.id == dealer_id:
                current_dealer_name = dealer.full_name
        context["dealer_id"] = dealer_id
        context["dealer_name"] = current_dealer_name
        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == "POST" and request.user.is_authenticated:
        review = {}
        #review["name"] = request.user.username
        review["name"] = request.user.username
        review["dealership"] = dealer_id
        review["review"] = request.POST["content"]
        if request.POST["purchasecheck"] == "on":
            review["purchase"] = "true"
        else:
            review["purchase"] = "false"
        review["purchase_date"] = request.POST["purchasedate"]
        car = request.POST["car"]
        car_object = CarModel.objects.get(pk=car)
        review["car_make"] = car_object.car_make.name
        review["car_model"] = car_object.name
        review["car_year"] = int(car_object.year.strftime("%Y"))
        review["id"] = 1114
        json_payload = {}
        json_payload["review"] = review

        response = post_request(url=post_review_url, payload=json_payload, dealerId=dealer_id)

        return redirect('djangoapp:dealer_details', dealer_id=dealer_id)
