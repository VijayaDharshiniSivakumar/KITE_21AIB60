from django.db import models

class stock(models.Model):
  name = models.CharField(max_length=255)
  value = models.IntegerField()