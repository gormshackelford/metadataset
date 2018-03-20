# Generated by Django 2.0 on 2018-02-26 19:11

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mptt.fields
import publications.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', publications.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Crop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crop', models.CharField(max_length=126)),
                ('slug', models.SlugField(max_length=254)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='publications.Crop')),
            ],
        ),
        migrations.CreateModel(
            name='Design',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('design', models.CharField(max_length=62, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExperimentCrop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.Crop')),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='ExperimentDesign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('design', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.Design')),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='ExperimentLatLong',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField(validators=[django.core.validators.MinValueValidator(-90.0), django.core.validators.MaxValueValidator(90.0)])),
                ('longitude', models.FloatField(validators=[django.core.validators.MinValueValidator(-180.0), django.core.validators.MaxValueValidator(180.0)])),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='ExperimentPopulation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='ExperimentPopulationOutcome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comparison', models.TextField(blank=True, null=True)),
                ('effect', models.IntegerField(blank=True, choices=[(1, '+'), (0, '0'), (-1, '-')], null=True)),
                ('effect_size', models.FloatField(blank=True, null=True)),
                ('effect_size_unit', models.CharField(blank=True, choices=[('g', "g - Hedges' g (standardized mean difference)"), ('R', 'R - Response ratio'), ('L', 'L - Log response ratio'), ('Zr', "Zr - Fischer's Z-transformed r"), ('Other', 'Other')], max_length=30, null=True)),
                ('other_effect_size_unit', models.CharField(blank=True, max_length=62, null=True)),
                ('lower_limit', models.FloatField(blank=True, help_text='Lower limit of the confidence interval for the effect size', null=True)),
                ('upper_limit', models.FloatField(blank=True, help_text='Upper limit of the confidence interval for the effect size', null=True)),
                ('confidence', models.FloatField(blank=True, help_text='Confidence of the confidence interval (percent)', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('se', models.FloatField(blank=True, help_text='Standard error of the effect size', null=True)),
                ('variance', models.FloatField(blank=True, help_text='Variance of the effect size', null=True)),
                ('n', models.IntegerField(blank=True, help_text='Number of replicates', null=True)),
                ('approximate_p_value', models.CharField(blank=True, choices=[('< 0.0001', '< 0.0001'), ('< 0.001', '< 0.001'), ('< 0.01', '< 0.01'), ('< 0.05', '< 0.05'), ('< 0.1', '< 0.1'), ('> 0.05', '> 0.05'), ('> 0.1', '> 0.1')], max_length=14, null=True)),
                ('exact_p_value', models.FloatField(blank=True, help_text='Please enter a value from 0 to 1.', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('z_value', models.FloatField(blank=True, null=True)),
                ('treatment_mean', models.IntegerField(blank=True, null=True)),
                ('control_mean', models.IntegerField(blank=True, null=True)),
                ('unit', models.CharField(blank=True, max_length=62, null=True)),
                ('n_treatment', models.IntegerField(blank=True, null=True)),
                ('n_control', models.IntegerField(blank=True, null=True)),
                ('sd_treatment', models.FloatField(blank=True, null=True)),
                ('sd_control', models.FloatField(blank=True, null=True)),
                ('se_treatment', models.FloatField(blank=True, null=True)),
                ('se_control', models.FloatField(blank=True, null=True)),
                ('sed', models.FloatField(blank=True, help_text='Standard error of the difference between the means', null=True)),
                ('lsd', models.FloatField(blank=True, help_text='Least significant difference between the means', null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('experiment_population', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.ExperimentPopulation')),
            ],
        ),
        migrations.CreateModel(
            name='Intervention',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intervention', models.CharField(max_length=254)),
                ('slug', models.SlugField(max_length=510)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='publications.Intervention')),
            ],
        ),
        migrations.CreateModel(
            name='Outcome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('outcome', models.CharField(max_length=254)),
                ('slug', models.SlugField(max_length=510)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='publications.Outcome')),
            ],
        ),
        migrations.CreateModel(
            name='Population',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('population', models.CharField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_is_confirmed', models.BooleanField(default=False)),
                ('institution', models.CharField(blank=True, max_length=254)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=510)),
                ('abstract', models.TextField(blank=True)),
                ('authors', models.TextField(blank=True)),
                ('year', models.CharField(blank=True, max_length=30)),
                ('journal', models.CharField(blank=True, max_length=510)),
                ('volume', models.CharField(blank=True, max_length=30)),
                ('issue', models.CharField(blank=True, max_length=30)),
                ('pages', models.CharField(blank=True, max_length=30)),
                ('doi', models.CharField(blank=True, max_length=510)),
                ('url', models.CharField(blank=True, max_length=510)),
                ('publisher', models.CharField(blank=True, max_length=510)),
                ('place', models.CharField(blank=True, max_length=510)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='experimentpopulationoutcome',
            name='outcome',
            field=mptt.fields.TreeForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.Outcome'),
        ),
        migrations.AddField(
            model_name='experimentpopulation',
            name='old_population',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='publications.Population'),
        ),
        migrations.AddField(
            model_name='experimentpopulation',
            name='population',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiment_population', to='publications.Population'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='intervention',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.Intervention'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='publication',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.Publication'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='outcome',
            unique_together={('slug', 'parent')},
        ),
        migrations.AlterUniqueTogether(
            name='intervention',
            unique_together={('slug', 'parent')},
        ),
        migrations.AlterUniqueTogether(
            name='experimentcrop',
            unique_together={('experiment', 'crop')},
        ),
        migrations.AlterUniqueTogether(
            name='crop',
            unique_together={('slug', 'parent')},
        ),
    ]
