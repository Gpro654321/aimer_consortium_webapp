from django.db import models

class State(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]  # Sort states alphabetically

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="districts")

    class Meta:
        ordering = ["name"]  # Sort districts alphabetically
        unique_together = ("name", "state")  # Ensure district names are unique per state

    def __str__(self):
        return f"{self.name}, {self.state.name}"
