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
from publications.models import Assessment, AssessmentStatus, Coordinates, Date, EAV, Experiment, PublicationPopulation, Study, Subject, User, XCountry


"""
Specify a user and a subject before running this script. This script deletes all
work that this user has done on this subject. For example, run this script after
copying the work of this user to another user (after running
copy_from_user_to_user.py), when merging the work of two people who have worked
together for Kappa analysis.
"""

# Specify the subject.
subject = "cassava"
subject = Subject.objects.get(subject=subject)

# Specify the user.
user = "ges47@cam.ac.uk"
user = User.objects.get(email=user)


assessment_status = AssessmentStatus.objects.filter(subject=subject, user=user)
assessments = Assessment.objects.filter(subject=subject, user=user)
experiments = Experiment.objects.filter(user=user, publication__subject=subject)
publication_populations = PublicationPopulation.objects.filter(user=user, publication__subject=subject)
coordinates = Coordinates.objects.filter(user=user, publication_index__subject=subject)
dates = Date.objects.filter(user=user, publication_index__subject=subject)
xcountries = XCountry.objects.filter(user=user, publication_index__subject=subject)
studies = Study.objects.filter(user=user, publication_index__subject=subject)
eavs = EAV.objects.filter(user=user, publication_index__subject=subject)


with transaction.atomic():
    assessment_status.delete()
    assessments.delete()
    experiments.delete()
    publication_populations.delete()
    coordinates.delete()
    dates.delete()
    xcountries.delete()
    studies.delete()
    eavs.delete()
