# Generated by Django 2.1.1 on 2018-10-30 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bfm_app', '0002_auto_20181030_1324'),
    ]

    operations = [
        migrations.AddField(
            model_name='benchmark',
            name='repeats',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
