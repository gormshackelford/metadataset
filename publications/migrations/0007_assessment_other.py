# Generated by Django 2.0 on 2018-07-20 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0006_auto_20180720_0908'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='other',
            field=models.BooleanField(default=False),
        ),
    ]
