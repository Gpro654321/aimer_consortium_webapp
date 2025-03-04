# Generated by Django 5.1.4 on 2025-01-21 04:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0006_alter_participant_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registrationtype',
            name='price',
        ),
        migrations.AddField(
            model_name='participant',
            name='is_aimer_member',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='registrationtype',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.CreateModel(
            name='WorkshopPricing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('early_bird_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('regular_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('aimer_member_price', models.DecimalField(blank=True, decimal_places=2, help_text='Price for AIMER members (leave blank if not applicable)', max_digits=10, null=True)),
                ('cut_off_date', models.DateField(blank=True, null=True)),
                ('workshop_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.registrationtype')),
            ],
        ),
    ]
