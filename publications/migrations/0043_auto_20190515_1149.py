# Generated by Django 2.0 on 2019-05-15 11:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0042_data_study_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Study',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study_id', models.IntegerField(blank=True, null=True)),
                ('study_name', models.CharField(blank=True, max_length=60, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('experiment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='name_experiment', to='publications.Experiment')),
                ('experiment_index', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='name_experiment_index', to='publications.Experiment')),
                ('outcome', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='name_outcome', to='publications.ExperimentPopulationOutcome')),
                ('outcome_index', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='name_outcome_index', to='publications.ExperimentPopulationOutcome')),
                ('population', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='name_population', to='publications.ExperimentPopulation')),
                ('population_index', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='name_population_index', to='publications.ExperimentPopulation')),
                ('publication', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='name_publication', to='publications.Publication')),
                ('publication_index', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='name_publication_index', to='publications.Publication')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='data',
            name='study_name',
        ),
    ]
