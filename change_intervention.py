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

from publications.models import User, Experiment, Intervention

user = User.objects.get(email="ges47@cam.ac.uk")

intervention_name = "Selecting and preparing the planting material"
old_intervention = Intervention.objects.get(intervention=intervention_name)

intervention_name = "Planting a different variety/cultivar (e.g., a disease-resistant variety)"
new_intervention = Intervention.objects.get(intervention=intervention_name)

experiments = Experiment.objects.filter(intervention=old_intervention, user=user)
print(experiments.count())
for experiment in experiments:
    print(experiment.id)
    print(experiment.intervention)
    experiment.intervention = new_intervention
    experiment.save()
    print(experiment.intervention)
