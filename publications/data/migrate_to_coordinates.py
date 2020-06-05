from django.db import transaction
from publications.models import Coordinates, ExperimentLatLong, Publication, PublicationLatLong, PublicationLatLongDMS


# First, run migrations 29 and 30 to migrate ExperimentLatLongDMS to Coordinates.
# Then run this script to migrate the data from the old models. Then run
# migration 31 to delete the old models.

# Coordinates was formerly ExperimentLatLongDMS. Here we are combining data from
# four models into one: ExperimentLatLongDMS, PublicationLatLongDMS,
# ExperimentLatLong, and PublicationLatLong.
coordinates = Coordinates.objects.all()
coordinates.count()

with transaction.atomic():
    # Add publication_index to existing instances.
    for x in coordinates:
        experiment = x.experiment
        publication = Publication.objects.get(experiment=experiment)
        x.publication_index = publication
        x.save()

coordinates = Coordinates.objects.all()
coordinates.count()


# Forgot to assign experiment_index to instances with experiment:
c = Coordinates.objects.all()
c.count()
with transaction.atomic():
    for x in c:
        if (x.experiment_index is None and x.experiment is not None):
            x.experiment_index = x.experiment
            x.save()

c = Coordinates.objects.all()
c.count()
for x in c:
    if (x.experiment_index is None and x.experiment is not None):
        print(x.experiment.pk)


publication_lat_long_dms = PublicationLatLongDMS.objects.all()
publication_lat_long_dms.count()

with transaction.atomic():
    # Create an instance for each instance in publication_lat_long_dms.
    for x in publication_lat_long_dms:
        instance = Coordinates(
            publication = x.publication,
            publication_index = x.publication,
            latitude_degrees = x.latitude_degrees or None,
            latitude_minutes = x.latitude_minutes or None,
            latitude_seconds = x.latitude_seconds or None,
            latitude_direction = x.latitude_direction,
            longitude_degrees = x.longitude_degrees or None,
            longitude_minutes = x.longitude_minutes or None,
            longitude_seconds = x.longitude_seconds or None,
            longitude_direction = x.longitude_direction
        )
        instance.save()

coordinates = Coordinates.objects.all()
coordinates.count()

coordinates.filter(publication_index = None).count()
for x in coordinates:
    print(x.publication_index.pk or None)

publication_lat_long = PublicationLatLong.objects.all()
publication_lat_long.count()

with transaction.atomic():
    # Create an instance for each instance in publication_lat_long.
    for x in publication_lat_long:
        if (x.longitude is not None and x.latitude is not None):
            instance = Coordinates(
                publication = x.publication,
                publication_index = x.publication
            )
            if (x.latitude < 0):
                instance.latitude_degrees = abs(x.latitude)
                instance.latitude_direction = "S"
            if (x.latitude >= 0):
                instance.latitude_degrees = x.latitude
                instance.latitude_direction = "N"
            if (x.longitude < 0):
                instance.longitude_degrees = abs(x.longitude)
                instance.longitude_direction = "W"
            if (x.longitude >= 0):
                instance.longitude_degrees = x.longitude
                instance.longitude_direction = "E"
            instance.save()

coordinates = Coordinates.objects.all()
coordinates.count()

experiment_lat_long = ExperimentLatLong.objects.all()
experiment_lat_long.count()

with transaction.atomic():
    # Create an instance for each instance in experiment_lat_long.
    for x in experiment_lat_long:
        if (x.longitude is not None and x.latitude is not None):
            instance = Coordinates(
                experiment = x.experiment,
                experiment_index = x.experiment
            )
            publication = Publication.objects.get(experiment=x.experiment)
            instance.publication_index = publication
            if (x.latitude < 0):
                instance.latitude_degrees = abs(x.latitude)
                instance.latitude_direction = "S"
            if (x.latitude >= 0):
                instance.latitude_degrees = x.latitude
                instance.latitude_direction = "N"
            if (x.longitude < 0):
                instance.longitude_degrees = abs(x.longitude)
                instance.longitude_direction = "W"
            if (x.longitude >= 0):
                instance.longitude_degrees = x.longitude
                instance.longitude_direction = "E"
            instance.save()

coordinates = Coordinates.objects.all()
coordinates.count()
