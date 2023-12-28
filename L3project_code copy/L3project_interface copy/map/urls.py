from django.urls import path
from . import views

# urlconf
urlpatterns = [
    path('index/', views.index),
    path('show/', views.show),
    path('option/', views.option)
]
