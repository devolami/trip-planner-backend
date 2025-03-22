from django.db import models

class LogEntry(models.Model):
   current_cycle_hour = models.CharField(max_length=2)
   total_driving_time = models.CharField(max_length=250)
   pickup_time = models.CharField(max_length=250)
   total_distance_miles = models.CharField(max_length=250)

   def __str__(self):
        return f"{self.current_cycle_hour}:00"
