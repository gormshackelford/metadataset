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
from django.urls import reverse
from publications.models import Attribute, EAV, Publication, Subject


domain = "http://127.0.0.1:8000"
# domain = "https://www.metadataset.com"


"""
Specify a subject, attribute, NA_value, and delete_NA() function.
"""

# Specify the subject. If this is a subject with children (e.g., "invasive
# species") then all of its children must have the same attributes as it does.
subject = "invasive species"
#subject = "japanese knotweed"
subject = Subject.objects.get(subject=subject)
subjects = subject.get_descendants(include_self=True)

# Specify the attribute. This must be a numeric attribute (i.e. an attribute
# with "value_as_number", not "value_as_factor").
attribute = "3.04 Time since management intervention"
attributes = Attribute.objects.get(pk=subject.attribute.pk).get_children()
attributes = attributes.get(attribute=attribute)
# Or the root attribute for this subject, if you want to delete the same NA
# value from all attributes for this subject.
attributes = Attribute.objects.get(pk=subject.attribute.pk).get_children()

# Specify the NA value.
NA_value = -999


with transaction.atomic():
    for subject in subjects:
        publications = Publication.objects.filter(subject=subject)
        for attribute in attributes:
            eavs = EAV.objects.filter(attribute=attribute, publication_index__in=publications)
            for eav in eavs:
                if (eav.value_as_number == NA_value):
                    path = reverse('publication', args=(), kwargs={
                        'subject': subject.slug,
                        'publication_pk': eav.publication_index.pk
                    })
                    user = eav.user
                    print(user, "---", attribute)
                    print(domain + path)
                    eav.delete()
