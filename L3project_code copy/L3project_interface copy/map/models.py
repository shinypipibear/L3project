from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


vehicle_type_choices =[
    ('', 'Choose..'),
    ('2', 'Motorcycle 50cc and under'),
    ('3', 'Motorcycle 125cc and under'),
    ('4', 'Motorcycle over 125cc and up to 500cc'),
    ('5', 'Motorcycle over 500cc'),
    ('8', 'Taxi/Private hire car'),
    ('9', 'Car'),
    ('10', 'Minibus (8 - 16 passenger seats)'),
    ('11', 'Bus or coach (17 or more pass seats)'),
    ('17', 'Agricultural vehicle'),
    ('19', 'Van / Goods 3.5 tonnes mgw or under'),
    ('20', 'Goods over 3.5t. and under 7.5t'),
    ('21', 'Goods 7.5 tonnes mgw and over'),
    ('23', 'Electric motorcycle'),
    ('97','Motorcycle - unknown cc'),
    ('98','Goods vehicle - unknown weight'),
    ('90', 'Other')
]

sex_of_driver_choices = [
    ('', 'Choose..'),
    ('1', 'Male'),
    ('2', 'Female')
]

age_band_of_driver_choices = [
    ('', 'Choose..'),
    ('4', '16 - 20'),
    ('5', '21 - 25'),
    ('6', '26 - 35'),
    ('7', '36 - 45'),
    ('8', '46 - 55'),
    ('9', '56 - 65'),
    ('10', '66 - 75'),
    ('11','Over 75')
]

driver_home_area_type_choices = [
    ('', 'Choose..'),
    ('1', 'Urban area'),
    ('2', 'Small town'),
    ('3', 'Rural')
]

places = [
    ('Canary Wharf', 'Canary Wharf'),
    ('Buckingham Palace', 'Buckingham Palace'),
    ('Big Ben','Big Ben'),
    ('Tower of London','Tower of London'),
    ('Tower Bridge','Tower Bridge'),
    ('Westminster Abbey', 'Westminster Abbey'),
    ('The British Museum','The British Museum'),
    ('The National Gallery','The National Gallery'),
    ('Trafalgar Square','Trafalgar Square'),
    ('Kensington Palace','Kensington Palace'),
    ('Hyde Park','Hyde Park'),
    ('Victoria and Albert Museum','Victoria and Albert Museum'),
    ('The Shard','The Shard'),
    ('Natural History Museum','Natural History Museum'),
    ('London Zoo','London Zoo'),
    ('Borough Market','Borough Market')
]


class User_input(models.Model):
    name = models.CharField(max_length=10, null=True)
    vehicle_type = models.CharField(max_length=10, choices=vehicle_type_choices,null=True)
    sex_of_driver = models.CharField(max_length=10, choices=sex_of_driver_choices,null=True)
    age_band_of_driver= models.CharField(max_length=10, choices=age_band_of_driver_choices,null=True)
    engine_capacity_cc= models.IntegerField(validators=[MaxValueValidator(99999),MinValueValidator(1)], null=True)
    driver_home_area_type= models.CharField(max_length=10, choices=driver_home_area_type_choices,null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User_option(models.Model):
    origin = models.CharField(max_length=30,choices=places, null=True)
    destination = models.CharField(max_length=30,choices=places, null=True)

    def __str__(self):
        return self.origin
