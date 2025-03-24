from django.urls import path
from .views import verify_certificate

urlpatterns = [
    path('verify/', verify_certificate, name='verify_certificate'),
]
