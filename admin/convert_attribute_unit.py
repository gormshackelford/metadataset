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
Specify a subject, attribute, new unit, new note, and convert_unit() function.
"""

# Specify the subject. If this is a subject with children (e.g., "invasive
# species") then all of its children must have the same attributes as it does.
subject = "invasive species"

# Specify the attribute. This must be a numeric attribute (i.e. an attribute
# with "value_as_number", not "value_as_factor").
attribute = "3.04 Time since management intervention"

# Specify the new unit for this attribute.
new_unit = "days"

# Specify the new note for this attribute (or specify "" to keep the old note).
new_note = "Number of days after intervention for which results were monitored"


# Specify the equation for converting from the old unit to the new unit.
def convert_unit(old_value):
    # Specify a condition to test for NA values (e.g., "-999"):
    if (old_value < 0):  # Example for "-999" for NA and positive values for not NA
        new_value = None  # Or -999 to keep the old NA value, for example.
    else:
        # Specify the equation:
        new_value = old_value * 365  # Example for converting from years to days
        new_value = round(new_value)
    return(new_value)


with transaction.atomic():
    subject = Subject.objects.get(subject=subject)
    attributes = Attribute.objects.get(pk=subject.attribute.pk).get_children()
    attribute = attributes.get(attribute=attribute)
    subjects = subject.get_descendants(include_self=True)
    for subject in subjects:
        publications = Publication.objects.filter(subject=subject)
        eavs = EAV.objects.filter(attribute=attribute, publication_index__in=publications)
        for eav in eavs:
            path = reverse('publication', args=(), kwargs={
                'subject': subject.slug,
                'publication_pk': eav.publication_index.pk
            })
            user = eav.user
            print(user)
            print(domain + path)

            print(eav.value_as_number)
            eav.value_as_number = convert_unit(eav.value_as_number)
            print(eav.value_as_number)
            eav.save()
            # Optional: delete this instance if it is None (see convert_unit()).
            if (eav.value_as_number is None):
                 eav.delete()

    print("Old attribute unit:", attribute.unit)
    print("Old attribute note:", attribute.note)

    attribute.unit = new_unit
    if (new_note != ""):
        attribute.note = new_note
    attribute.save()

    print("New attribute unit:", attribute.unit)
    print("New attribute note:", attribute.note)
