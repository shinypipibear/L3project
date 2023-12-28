from django import forms
from .models import User_input, User_option


class User_inputForm(forms.ModelForm):
    class Meta:
        model = User_input
        fields = ['name','vehicle_type','sex_of_driver','age_band_of_driver','engine_capacity_cc', 'driver_home_area_type']


class User_optionForm(forms.ModelForm):
    class Meta:
        model = User_option
        fields = ['origin', 'destination']
