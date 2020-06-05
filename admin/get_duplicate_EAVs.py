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


from django.urls import reverse
from publications.models import User, Subject, UserSubject, Attribute, EAV, Publication, Experiment, ExperimentPopulation, ExperimentPopulationOutcome


domain = "https://www.metadataset.com"
#domain = "http://127.0.0.1:8000"


subjects = Subject.objects.all().order_by('-subject')
for subject in subjects:
    print(subject)

    if (subject.attribute):
        atts = Attribute.objects.get(pk=subject.attribute.pk).get_children().order_by('attribute')
        user_subjects = UserSubject.objects.filter(subject=subject)
        users = User.objects.filter(usersubject__in=user_subjects)

        pubs = Publication.objects.filter(subject=subject)
        for pub in pubs:
            if EAV.objects.filter(publication=pub).exists():
                for att in atts:
                    for user in users:
                        eavs = EAV.objects.filter(attribute=att, publication=pub, user=user)
                        if eavs.count() > 1:

                            path = reverse('metadata', args=(), kwargs={
                                'subject': subject.slug,
                                'publication_pk': pub.pk
                            })

                            print(user, "---", att)
                            print(domain + path)


        exps = Experiment.objects.filter(publication__in=pubs)
        for exp in exps:
            if EAV.objects.filter(experiment=exp).exists():
                for att in atts:
                    eavs = EAV.objects.filter(attribute=att, experiment=exp)
                    if eavs.count() > 1:

                        pub = exp.publication
                        user = exp.user

                        experiment_index_list = Experiment.objects.filter(
                            publication=pub.pk, user=user
                        ).order_by('pk').values_list('pk', flat=True)
                        experiment_index = list(experiment_index_list).index(exp.pk)

                        path = reverse('experiment', args=(), kwargs={
                            'subject': subject.slug,
                            'publication_pk': exp.publication.pk,
                            'experiment_index': experiment_index
                        })

                        print(user, "---", att)
                        print(domain + path)


        pops = ExperimentPopulation.objects.filter(experiment__in=exps)
        for pop in pops:
            if EAV.objects.filter(population=pop).exists():
                for att in atts:
                    eavs = EAV.objects.filter(attribute=att, population=pop)
                    if eavs.count() > 1:

                        exp = pop.experiment
                        pub = exp.publication
                        user = exp.user

                        experiment_index_list = Experiment.objects.filter(
                            publication=pub.pk, user=user
                        ).order_by('pk').values_list('pk', flat=True)
                        experiment_index = list(experiment_index_list).index(exp.pk)

                        population_index_list = ExperimentPopulation.objects.filter(
                            experiment=exp, experiment__user=user
                        ).order_by('pk').values_list('pk', flat=True)
                        population_index = list(population_index_list).index(pop.pk)

                        path = reverse('population', args=(), kwargs={
                            'subject': subject.slug,
                            'publication_pk': pub.pk,
                            'experiment_index': experiment_index,
                            'population_index': population_index
                        })

                        print(user, "---", att)
                        print(domain + path)


        outs = ExperimentPopulationOutcome.objects.filter(experiment_population__experiment__in=exps)
        for out in outs:
            if EAV.objects.filter(outcome=out).exists():
                for att in atts:
                    eavs = EAV.objects.filter(attribute=att, outcome=out)
                    if eavs.count() > 1:

                        pop = out.experiment_population
                        exp = pop.experiment
                        pub = exp.publication
                        user = exp.user

                        experiment_index_list = Experiment.objects.filter(
                            publication=pub.pk, user=user
                        ).order_by('pk').values_list('pk', flat=True)
                        experiment_index = list(experiment_index_list).index(exp.pk)

                        population_index_list = ExperimentPopulation.objects.filter(
                            experiment=exp, experiment__user=user
                        ).order_by('pk').values_list('pk', flat=True)
                        population_index = list(population_index_list).index(pop.pk)

                        outcome_index_list = ExperimentPopulationOutcome.objects.filter(
                            experiment_population=pop, experiment_population__experiment__user=user
                        ).order_by('pk').values_list('pk', flat=True)
                        outcome_index = list(outcome_index_list).index(out.pk)

                        path = reverse('outcome', args=(), kwargs={
                            'subject': subject.slug,
                            'publication_pk': pub.pk,
                            'experiment_index': experiment_index,
                            'population_index': population_index,
                            'outcome_index': outcome_index
                        })

                        print(user, "---", att)
                        print(domain + path)
