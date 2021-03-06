# Generated by Django 2.0 on 2020-06-04 08:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0052_auto_20200323_1247'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attribute',
            options={'ordering': ['attribute']},
        ),
        migrations.AlterUniqueTogether(
            name='eav',
            unique_together={('attribute', 'user', 'population'), ('attribute', 'user', 'experiment'), ('attribute', 'user', 'publication'), ('attribute', 'user', 'outcome')},
        ),
    ]
