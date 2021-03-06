# Generated by Django 2.0 on 2019-02-04 14:11

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0017_auto_20180830_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='level',
            field=models.PositiveIntegerField(db_index=True, default=1, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subject',
            name='lft',
            field=models.PositiveIntegerField(db_index=True, default=1, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subject',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='publications.Subject'),
        ),
        migrations.AddField(
            model_name='subject',
            name='rght',
            field=models.PositiveIntegerField(db_index=True, default=2, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subject',
            name='tree_id',
            field=models.PositiveIntegerField(db_index=True, default=1, editable=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='experimentcountry',
            name='experiment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiment_countries', to='publications.Experiment'),
        ),
        migrations.AlterField(
            model_name='experimentdate',
            name='experiment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiment_dates', to='publications.Experiment'),
        ),
        migrations.AlterField(
            model_name='experimentdesign',
            name='experiment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiment_designs', to='publications.Experiment'),
        ),
        migrations.AlterField(
            model_name='experimentlatlong',
            name='experiment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiment_latlongs', to='publications.Experiment'),
        ),
    ]
