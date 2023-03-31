import requests
import json
import os
from dotenv import load_dotenv
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

load_dotenv()

def get_request(url, api_key="", **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        if api_key:
            print("HEY")
            response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'}, auth=HTTPBasicAuth('apikey', api_key))
        else:
            print("HMM")
            response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'})
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    print(payload)
    response = requests.post(url, params=kwargs, json=payload)
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # For each dealer object
        for dealer in json_result:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealerId):
    results = []

    json_result = get_request(url, dealerId=dealerId)["data"]["docs"]
    if json_result:
        for review in json_result:
            try:
                sentiment = review["sentiment"]
            except:
                sentiment = analyze_review_sentiments(review["review"])
            
            review_obj = DealerReview(id=review["id"], name=review["name"], dealership=review["dealership"], review=review["review"], purchase=review["purchase"], purchase_date=review["purchase_date"], car_make=review["car_make"], car_model=review["car_model"], car_year=review["car_year"], sentiment=sentiment)

            print(review_obj.sentiment)
            results.append(review_obj)
    
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    watson_nlu_url = os.environ['watson_nlu_url']
    watson_nlu_apikey = os.environ['watson_nlu_apikey']
    watson_nlu_version = os.environ['watson_nlu_version']

    authenticator = IAMAuthenticator(watson_nlu_apikey)

    natural_language_understanding = NaturalLanguageUnderstandingV1(version=watson_nlu_version,authenticator=authenticator)

    natural_language_understanding.set_service_url(watson_nlu_url)

    try:
        response = natural_language_understanding.analyze( text=text ,features=Features(sentiment=SentimentOptions(targets=[text]))).get_result()
        sentiment = response['sentiment']['document']['label']
    except:
        # Sometimes the given text is too short to be analyzed by
        # Watson NLU service. In this case we set the sentiment to
        # neutral.
        sentiment = "neutral"

    return sentiment
