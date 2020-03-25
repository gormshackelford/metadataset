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
from publications.models import Assessment, Subject, User


"""
This script marks as not completed ('is_completed == False') all publications
that have been included at Stage 2 ('full_text_is_relevant == True'). Specify a
subject and a user before running this script.
"""

# Specify a subject.
subject = "cassava"
subject = Subject.objects.get(subject=subject)

# Specify a user.
user = "cassava@metadataset.com"
user = User.objects.get(email=user)


i = 0

assessments = Assessment.objects.filter(
    subject=subject,
    user=user,
    full_text_is_relevant=True,
    is_completed=True
)
print("Number to be changed:", assessments.count())

with transaction.atomic():
    for assessment in assessments:
        assessment.is_completed = False
        assessment.save()
        i = i + 1

print("Number changed:", i)
