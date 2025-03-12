from django.db import models

class SensorData(models.Model):
    timestamp = models.DateTimeField()
    temperature = models.FloatField(null=True, blank=True)  
    humidity = models.FloatField(null=True, blank=True)
    air_quality = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.timestamp} - Temp: {self.temperature}, Humidity: {self.humidity}, Air Quality: {self.air_quality}"
