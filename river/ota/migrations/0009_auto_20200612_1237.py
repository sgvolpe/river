# Generated by Django 3.0.3 on 2020-06-12 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ota', '0008_auto_20200611_2047'),
    ]

    operations = [
        migrations.AddField(
            model_name='itinerary',
            name='cabins',
            field=models.CharField(blank=True, default='na', max_length=50),
        ),
        migrations.AddField(
            model_name='itinerary',
            name='rbds',
            field=models.CharField(blank=True, default='na', max_length=50),
        ),
    ]