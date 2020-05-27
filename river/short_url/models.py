from django.db import models
from django.urls import reverse
import base64


class ShortUrl(models.Model):
    original_url = models.URLField()
    encoded_url = models.URLField(default='www.google.com')
    name = models.CharField(max_length=200)

    def encode(self):
        encoded_bytes = base64.b64encode(self.original_url.encode("utf-8"))
        self.encoded_url = str(encoded_bytes, "utf-8")
        self.save()
        return self.pk
        #return self.encoded_url

    def decode(self):
        decoded_bytes = base64.b64decode(self.encoded_url)
        self.decoded_url = f'https://{str(decoded_bytes, "utf-8")}'
        self.save()
        return self.decoded_url





class Author(models.Model):
    name = models.CharField(max_length=200)

    def get_absolute_url(self):
        return reverse('author-detail', kwargs={'pk': self.pk})