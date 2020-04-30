# Generated by Django 2.1.1 on 2018-10-30 12:44

from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AncillariesComparison',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('bookings_file', models.FileField(upload_to='dashboard/static/booking_files/')),
                ('charts', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('Carriers', 'Carriers'), ('CarriersComplementary', 'CarriersComplementary'), ('Bookings', 'Bookings'), ('BookingsComplementary', 'BookingsComplementary')], max_length=61)),
                ('ancillaries', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('Seats', 'Seats'), ('Baggage', 'Baggage'), ('Pets', 'Pets'), ('Lounge', 'Lounge'), ('Meals', 'Meals'), ('Medical', 'Medical')], max_length=39)),
            ],
        ),
        migrations.CreateModel(
            name='DashApp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instance_name', models.CharField(blank=True, max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=110, unique=True)),
                ('base_state', models.TextField(default='{}')),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('save_on_change', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='IndividualDashboard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('csv_file', models.FileField(blank=True, upload_to='dashboard/static/individual_files/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('ond', models.CharField(blank=True, max_length=500)),
                ('ap_los', models.CharField(blank=True, max_length=500)),
                ('search_date', models.CharField(blank=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ShoppingComparison',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('csv_file', models.FileField(blank=True, upload_to='dashboard/static/absolute_files/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('onds', models.CharField(blank=True, max_length=500)),
                ('ap_los', models.CharField(blank=True, max_length=500)),
                ('analysis_finished', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StatelessApp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=110, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SummaryDashboard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('csv_file', models.FileField(blank=True, upload_to='dashboard/static/sumary_files/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('onds', models.CharField(blank=True, max_length=500)),
                ('ap_los', models.CharField(blank=True, max_length=500)),
            ],
        ),
        migrations.AddField(
            model_name='shoppingcomparison',
            name='summary_dashboard',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='s_dashboard', to='dashboard.SummaryDashboard'),
        ),
        migrations.AddField(
            model_name='individualdashboard',
            name='summary_dashboard',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='individual_dashboards', to='dashboard.SummaryDashboard'),
        ),
        migrations.AddField(
            model_name='dashapp',
            name='stateless_app',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dashboard.StatelessApp'),
        ),
    ]
