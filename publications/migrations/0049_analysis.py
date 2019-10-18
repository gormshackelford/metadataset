# Generated by Django 2.0 on 2019-09-27 17:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0048_publication_citation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('effect_size', models.FloatField(blank=True, null=True)),
                ('pval', models.FloatField(blank=True, null=True)),
                ('lb', models.FloatField(blank=True, null=True)),
                ('ub', models.FloatField(blank=True, null=True)),
                ('api_query_string', models.CharField(max_length=255)),
                ('shiny_bookmark', models.CharField(max_length=255)),
                ('user_settings', models.CharField(max_length=60)),
                ('there_was_an_error', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('intervention', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.Intervention')),
                ('outcome', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.Outcome')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.Subject')),
            ],
            options={
                'verbose_name_plural': 'analyses',
            },
        ),
    ]