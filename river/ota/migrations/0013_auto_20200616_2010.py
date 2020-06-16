# Generated by Django 3.0.3 on 2020-06-16 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ota', '0012_search_quickest_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='itinerary',
            name='passenger_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='itinerary',
            name='seat_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
