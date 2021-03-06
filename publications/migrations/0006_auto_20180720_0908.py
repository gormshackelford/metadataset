# Generated by Django 2.0 on 2018-07-20 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0005_auto_20180710_0922'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='cannot_access',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assessment',
            name='cannot_find',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assessment',
            name='no_comparator',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assessment',
            name='no_intervention',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assessment',
            name='no_outcome',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assessment',
            name='no_population',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assessment',
            name='secondary_literature',
            field=models.BooleanField(default=False),
        ),
    ]
