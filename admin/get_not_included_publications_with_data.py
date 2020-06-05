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
from publications.models import Assessment, Experiment, Publication, PublicationPopulation, Subject


"""
This script checks for publications that have been excluded or not assessed
but are still tagged with interventions or publication_populations (for safety,
these tags are not deleted if a publication is later excluded or reset).
Specify a subject before running this script.
"""

# Specify a subject.
subject = "cassava"
subject = Subject.objects.get(subject=subject)

experiments = Experiment.objects.filter(publication__subject=subject)

included = Assessment.objects.filter(
    subject=subject,
    full_text_is_relevant=True
)

publications = Publication.objects.filter(subject=subject)

not_included_publications = publications.exclude(assessment__in=included)
not_included_publications_with_interventions = not_included_publications.filter(
    experiment__in=experiments
).distinct()
print("Number of publications still with interventions:", not_included_publications_with_interventions.count())
for publication in not_included_publications_with_interventions:
    print(publication.pk)

publication_populations = PublicationPopulation.objects.filter(publication__subject=subject)
not_included_publications_with_publication_populations = not_included_publications.filter(
    publicationpopulation__in=publication_populations
).distinct()
print("Number of publications still with publication_populations:", not_included_publications_with_publication_populations.count())
for publication in not_included_publications_with_publication_populations:
    print(publication.pk)
