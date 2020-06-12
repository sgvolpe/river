# Generated by Django 3.0.3 on 2020-06-11 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ota', '0006_auto_20200611_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='passenger',
            name='profile_id',
            field=models.CharField(default='0', max_length=2),
        ),
        migrations.AddField(
            model_name='passenger',
            name='reservation_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ota.Reservation'),
        ),
    ]