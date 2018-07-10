# Generated by Django 2.0 on 2018-07-03 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0002_auto_20180703_1340'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=255)),
                ('un_m49', models.IntegerField(blank=True, null=True)),
                ('iso_alpha_3', models.CharField(blank=True, max_length=4, null=True)),
            ],
            options={
                'verbose_name_plural': 'countries',
            },
        ),
    ]