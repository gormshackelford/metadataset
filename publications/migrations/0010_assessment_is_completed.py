# Generated by Django 2.0 on 2018-07-23 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0009_assessmentstatus_next_full_text_assessment'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]
