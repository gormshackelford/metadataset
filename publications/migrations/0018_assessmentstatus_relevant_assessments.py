# Generated by Django 2.0 on 2018-06-06 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0017_assessmentstatus_completed_full_text_assessments'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessmentstatus',
            name='relevant_assessments',
            field=models.TextField(blank=True),
        ),
    ]
