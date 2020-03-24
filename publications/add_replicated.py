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
from publications.models import Design, Experiment, ExperimentDesign, Subject, User


"""
This script adds the experimental design 'replicated' to any experiment that is
already tagged as 'randomised' or 'blocked' (since these designs must be
'replicated', but they have sometimes accidentally not been tagged as
'replicated'). Specify a subject and a user before running this script.
"""

# Specify a subject.
subject = "cassava"
subject = Subject.objects.get(subject=subject)

# Specify a user.
user = "cassava@metadataset.com"
user = User.objects.get(email=user)


replicated = Design.objects.get(design="replicated")

i = 0

with transaction.atomic():
    experiments = Experiment.objects.filter(user=user, publication__subject=subject)
    for experiment in experiments:
        experiment_designs = ExperimentDesign.objects.filter(experiment=experiment)
        # If not "replicated"
        if experiment_designs.filter(design__design="replicated").exists() == False:
            # And if "randomised" or "blocked"
            if (experiment_designs.filter(design__design="randomised").exists()
                or experiment_designs.filter(design__design="blocked").exists()):
                # Add "replicated".
                instance = ExperimentDesign(experiment=experiment, design=replicated)
                instance.save()
                print("created:", instance.design.design)
                i = i + 1

print("i:", i)
