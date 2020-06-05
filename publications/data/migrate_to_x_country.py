from django.db import transaction
from publications.models import ExperimentCountry, Publication, PublicationCountry, XCountry


# First, run migrations 32 to create XCountry. Then run this script to migrate
# the data from the old models. Then run migration 33 to delete the old models.
xc = XCountry.objects.all()
xc.count()

publication_countries = PublicationCountry.objects.all()
publication_countries.count()

with transaction.atomic():
    for x in publication_countries:
        instance = XCountry(
            country = x.country,
            publication = x.publication,
            publication_index = x.publication,
            user = x.user
        )
        instance.save()

xc = XCountry.objects.all()
xc.count()
xc.exclude(publication_index = None).count()
xc.filter(country__country = "Nigeria").count()

experiment_countries = ExperimentCountry.objects.all()
experiment_countries.count()

with transaction.atomic():
    for x in experiment_countries:
        instance = XCountry(
            country = x.country,
            experiment = x.experiment,
            experiment_index = x.experiment,
            publication_index = x.experiment.publication,
            user = x.experiment.user
        )
        instance.save()

xc = XCountry.objects.all()
xc.count()
xc.exclude(publication_index = None).count()
xc.exclude(country = None).count()
xc.filter(country__country = "Nigeria").count()
