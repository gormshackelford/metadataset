# Run this script as a "standalone" script (terminology from the Django
# documentation) that uses the Djano ORM to get data from the database.
# This requires django.setup(), which requires the settings for this project.
# Appending the root directory to the system path also prevents errors when
# importing the models from the app.
if __name__ == '__main__':
import sys
import os
import django
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
    os.path.pardir))
sys.path.append(parent_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metadataset.settings")
django.setup()

from django.db import transaction
from publications.models import Publication, Population, Outcome, Experiment, ExperimentPopulation

experiment_populations = ExperimentPopulation.objects.all()

with transaction.atomic():
    for experiment_population in experiment_populations:
        population = experiment_population.population
        new_population = Outcome.objects.get(outcome=population)
        experiment_population.new_population = new_population
        experiment_population.save()

with transaction.atomic():
    i = 1
    for experiment_population in experiment_populations:
        new_population = experiment_population.new_population
        print(i)
        print(new_population)
        i = i + 1
