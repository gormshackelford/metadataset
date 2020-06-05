from django.db import transaction
from publications.models import ExperimentDate, Publication, Date, Experiment


# First, run migrations 35 and 36 to rename PublicationDate to Date. Then run this
# script to migrate the data from the ExperimentDate to Date. Then run migration
# 37 to delete ExperimentDate.
d = Date.objects.all()
d.count()

d.filter(publication=None).count()
d.filter(publication_index=None).count()

with transaction.atomic():
    for instance in d:
        instance.publication_index = instance.publication
        instance.save()
d.filter(publication_index=None).count()



d = Date.objects.all()
d.count()

ed = ExperimentDate.objects.all()
ed.count()

ed.filter(experiment=None).count()

with transaction.atomic():
    for x in ed:
        instance = Date(
            start_year = x.year or None,
            start_month = x.month or None,
            start_day = x.day or None,
            experiment = x.experiment,
            experiment_index = x.experiment,
            publication_index = x.experiment.publication,
            user = x.experiment.user
        )
        instance.save()

d = Date.objects.all()
d.count()

d.exclude(experiment=None).count()
d.exclude(experiment_index=None).count()
d.exclude(publication_index=None).count()



p = Publication.objects.all()
p.count()
# Check that no publication has more than two dates.
for publication in p:
    dates = d.filter(publication=publication)
    if dates.count() > 2:
        print(publication)
        print(publication.pk)

e = Experiment.objects.all()
e.count()
# Check that no experiment has more than two dates.
for experiment in e:
    dates = d.filter(experiment=experiment)
    if dates.count() > 2:
        print(experiment.publication)
        print(experiment.publication.pk)



d = Date.objects.all()
d.count()
d.filter(end_year=None).count()
d.filter(start_year=None).count()
d.filter(start_year=None).delete()
d = Date.objects.all()
d.count()
d.filter(publication_index=None).count()



d = Date.objects.all()
d.count()

e = Experiment.objects.all()
e.count()

with transaction.atomic():
    for experiment in e:
        dates = d.filter(experiment=experiment)
        if dates.count() == 2:
            date0 = dates[0]
            date1 = dates[1]
            date0.end_year = date1.start_year or None
            date0.end_month = date1.start_month or None
            date0.end_day = date1.start_day or None
            date0.save()
            date1.delete()

for date in d.exclude(end_year=None):
    print(date.end_year)
    print(date.end_month)
    print(date.end_day)



d = Date.objects.all()
d.count()

p = Publication.objects.all()
p.count()

with transaction.atomic():
    for publication in p:
        dates = d.filter(publication=publication)
        if dates.count() == 2:
            date0 = dates[0]
            date1 = dates[1]
            date0.end_year = date1.start_year or None
            date0.end_month = date1.start_month or None
            date0.end_day = date1.start_day or None
            date0.save()
            date1.delete()

for date in d.exclude(end_year=None):
    print(date.end_year)
    print(date.end_month)
    print(date.end_day)

d.exclude(end_year=None).count()
