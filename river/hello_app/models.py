from django.db import models
from django.contrib.auth.models import User


class Webpage(models.Model):
    url = models.URLField(unique=True)


class AccessRecord(models.Model):
    name = models.ForeignKey(Webpage, on_delete=models.CASCADE,)
    date = models.DateField()

    def __str__(self):
        return str(self.date)


class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    portfolio_site = models.URLField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics',blank=True)

    def __str__(self):
        return self.user.username
