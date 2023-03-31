from django.db import models
from django.utils.timezone import now


# Create your models here.

class CarMake(models.Model):
    name = models.CharField(null=False, max_length=30, default='Name')
    description = models.CharField(null=False, max_length=256, default='Description')
    country_id = models.CharField(null=False, max_length=2, default='XX')

    def __str__(self):
        return "Name: " + self.name + "," + \
            "Description: " + self.description + "," + \
                "Contry: " + self.country_id

class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=128, default='Model')
    dealer_id = models.IntegerField(default=0)
    SUV = 'suv'
    WAGON = 'wagon'
    SEDAN = 'sedan'
    COUPE = 'coupe'
    CAR_TYPES = [
        (SUV, 'SUV'),
        (WAGON, 'Wagon'),
        (SEDAN, 'Sedan'),
        (COUPE, 'Coupe')
    ]
    type = models.CharField(max_length=128, choices=CAR_TYPES, default=COUPE)
    year = models.DateField(default=now)

    def __str__(self):
        return "Make: " + self.car_make.name + "," + \
            "Name: " + self.name + "," + \
                "Dealer: " + str(self.dealer_id) + "," + \
                    "Year: " + str(self.year)

class CarDealer:

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name

class DealerReview:

    def __init__(self, id, name, dealership, review, purchase, purchase_date, car_make, car_model, car_year, sentiment):
        self.id = id
        self.name = name
        self.dealership = dealership
        self.review = review
        self.purchase = purchase
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.sentiment = sentiment
    
    def __str__(self):
        return "Review id: " + self.id
