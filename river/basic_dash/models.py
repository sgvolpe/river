from django.db import models



class BasicDash(models.Model):
    title = models.CharField(max_length=50, blank=True)