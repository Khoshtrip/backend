# Generated by Django 4.2.17 on 2025-03-02 09:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('package', '0002_alter_trippackage_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='trippackage',
            name='rating',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='trippackage',
            name='ratings_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='trippackage',
            name='ratings_sum',
            field=models.FloatField(default=0.0),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('purchase_date', models.DateTimeField(blank=True, null=True)),
                ('card_number', models.CharField(blank=True, max_length=16, null=True)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='package.trippackage')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
