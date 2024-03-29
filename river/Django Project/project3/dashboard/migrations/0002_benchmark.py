# Generated by Django 2.1.1 on 2018-10-31 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Benchmark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('ap', models.CharField(blank=True, max_length=500)),
                ('los', models.CharField(blank=True, max_length=500)),
                ('onds', models.CharField(blank=True, max_length=500)),
                ('bfm_template_1', models.TextField(blank=True, null=True)),
                ('bfm_template_2', models.TextField(blank=True, null=True)),
                ('repeats', models.IntegerField()),
            ],
        ),
    ]
