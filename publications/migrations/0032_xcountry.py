# Generated by Django 2.0 on 2019-04-16 13:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0031_auto_20190416_1249'),
    ]

    operations = [
        migrations.CreateModel(
            name='XCountry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.Country')),
                ('experiment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='xcountry_experiment', to='publications.Experiment')),
                ('experiment_index', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='xcountry_experiment_index', to='publications.Experiment')),
                ('outcome', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='xcountry_outcome', to='publications.ExperimentPopulationOutcome')),
                ('outcome_index', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='xcountry_outcome_index', to='publications.ExperimentPopulationOutcome')),
                ('population', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='xcountry_population', to='publications.ExperimentPopulation')),
                ('population_index', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='xcountry_population_index', to='publications.ExperimentPopulation')),
                ('publication', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='xcountry_publication', to='publications.Publication')),
                ('publication_index', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='xcountry_publication_index', to='publications.Publication')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'xcountries',
            },
        ),
    ]