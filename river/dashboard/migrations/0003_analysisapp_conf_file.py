# Generated by Django 3.0.3 on 2020-04-28 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_analysisapp_df_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysisapp',
            name='conf_file',
            field=models.CharField(default='default.txt', max_length=200),
        ),
    ]
