from django.urls import path

from . import views  # Import views from your app's views.py

from . import api_views

urlpatterns = [
    path('', views.registration_view, name='registration'),
    path('payment_success/', views.payment_success, name='payment_success'),

    


    # API endpoints for autocomplete
    path("api/districts/", api_views.get_relevant_districts, name="get_districts"),
    path("api/states/", api_views.get_states, name="get_states"),

    # API endpoints for workshop details
    path("api/workshop-details/", api_views.get_workshop_details, name="get_workshop_details")

]
