from django.db import models

from .choices import registration_for_choices

# Create your models here.
class RegistrationType(models.Model):
    registration_for = models.CharField(max_length=400, choices=registration_for_choices)

