# Generated by Django 2.0 on 2018-05-29 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0011_outcome_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='intervention',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='publications.Intervention'),
        ),
    ]
