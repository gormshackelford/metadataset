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


from ast import literal_eval
from copy import deepcopy
from datetime import datetime
from django.db import transaction
from publications.models import Assessment, AssessmentStatus, Coordinates, Date, Experiment, ExperimentDesign, ExperimentPopulation, ExperimentPopulationOutcome, PublicationPopulation, PublicationPopulationOutcome, Study, Subject, User, XCountry


"""
This script copies the assessments from one user to another user, for a given
subject. This script should be run after all full texts have been assessed
(for example, if the person who did some or all of the full text assessments
is not the person who is entering the data for meta-analysis, or if two people
collaborated on the full text assessments, and these assessments now need to
be combined into one unified account. Specify a subject, user, and user_to_copy
before running this script.
"""


# Specify the subject.
subject = "cassava"

# Specify the users.
user = "cassava@metadataset.com"  # User to whom the assessments will be copied
user_to_copy = "ges47@cam.ac.uk"  # User from whom the assessments will be copied


"""
Uncomment one of these options. If 'merge_or_overwrite_included_full_texts ==
False' then publications that have been assessed as 'full_text_is_relevant ==
True' by the user will not be changed (unless 'is_completed == False' and
'full_text_is_relevant == True and 'is_completed == True' for the user to copy).
However, if 'merge_or_overwrite_included_full_texts == True' then all
publications that this user has assessed will be overwritten by the assessments
of the user_to_copy (if 'merge_or_overwrite == "overwrite"') or else the
they will be merged with those of the user (e.g., if the user assessed a full
text as relevant and selected one intervention, then the interventions,
populations, outcomes, and other metadata that were included by the user_to_copy
will be copied, even if these duplicate those that were already included by the
user. The recommended default settings are:
merge_or_overwrite_included_full_texts = False
merge_or_overwrite = "overwrite"
"""
#merge_or_overwrite_included_full_texts = True
merge_or_overwrite_included_full_texts = False

# Also choose one of these two options and comment the other. See above for an
# explanation.
#merge_or_overwrite = "merge"
merge_or_overwrite = "overwrite"


subject = Subject.objects.get(subject=subject)
user = User.objects.get(email=user)
user_to_copy = User.objects.get(email=user_to_copy)
assessments = Assessment.objects.filter(subject=subject, user=user)
assessments_to_copy = Assessment.objects.filter(subject=subject, user=user_to_copy)

start_time = datetime.now().time()
print(start_time)

with transaction.atomic():
    for assessment_to_copy in assessments_to_copy:
        now = datetime.now().time()
        print(now)
        assessment_status = AssessmentStatus.objects.get(subject=subject, user=user)
        completed_assessments = literal_eval(assessment_status.completed_assessments)
        publication = assessment_to_copy.publication
        publication_pk = int(publication.pk)

        # If this user has assessed this publication
        if assessments.filter(publication=publication).exists():
            assessment = assessments.get(publication=publication)
            if merge_or_overwrite_included_full_texts == False:
                # If this user has not assessed this full text
                if assessment.full_text_is_relevant is None:
                    # And the user_to_copy has assessed this full text
                    if assessment_to_copy.full_text_is_relevant is not None:
                        # Delete this assessment.
                        assessment.delete()
                        if publication_pk in completed_assessments:
                            completed_assessments.remove(publication_pk)
                            assessment_status.completed_assessments = completed_assessments
                            assessment_status.save()
                # Else if this user has excluded this full text
                elif assessment.full_text_is_relevant == False:
                    # And the user_to_copy has included this full text
                    if assessment_to_copy.full_text_is_relevant == True:
                        # Delete this assessment.
                        assessment.delete()
                        if publication_pk in completed_assessments:
                            completed_assessments.remove(publication_pk)
                            assessment_status.completed_assessments = completed_assessments
                            assessment_status.save()
                # Else if this user has included but not completed this full text
                elif assessment.full_text_is_relevant == True and assessment.is_completed == False:
                    # And the user_to_copy has included and completed this full text
                    if assessment_to_copy.full_text_is_relevant == True and assessment_to_copy.is_completed == True:
                        # Delete this assessment.
                        assessment.delete()
                        if publication_pk in completed_assessments:
                            completed_assessments.remove(publication_pk)
                            assessment_status.completed_assessments = completed_assessments
                            assessment_status.save()
                        if merge_or_overwrite == "overwrite":
                            # Delete experiments for this publication (and cascade to experiment_populations and experiment_population_outcomes).
                            experiments = Experiment.objects.filter(user=user, publication=publication)
                            experiments.delete()
                            # Delete publication_populations for this publication (and cascade).
                            publication_populations = PublicationPopulation.objects.filter(user=user, publication=publication)
                            publication_populations.delete()
                            # Delete instances linked to this user and publication (which is not deleted by the cascade from the deletion of experiment).
                            coordinates = Coordinates.objects.filter(user=user, publication=publication)
                            coordinates.delete()
                            dates = Date.objects.filter(user=user, publication=publication)
                            dates.delete()
                            xcountries = XCountry.objects.filter(user=user, publication=publication)
                            xcountries.delete()
            elif merge_or_overwrite_included_full_texts == True:
                # Delete this assessment.
                assessment.delete()
                if publication_pk in completed_assessments:
                    completed_assessments.remove(publication_pk)
                    assessment_status.completed_assessments = completed_assessments
                    assessment_status.save()
                if merge_or_overwrite == "overwrite":
                    # Delete experiments for this publication (and cascade to experiment_populations and experiment_population_outcomes).
                    experiments = Experiment.objects.filter(user=user, publication=publication)
                    experiments.delete()
                    # Delete publication_populations for this publication (and cascade).
                    publication_populations = PublicationPopulation.objects.filter(user=user, publication=publication)
                    publication_populations.delete()
                    # Delete instances linked to this user and publication (which is not deleted by the cascade from the deletion of experiment).
                    coordinates = Coordinates.objects.filter(user=user, publication=publication)
                    coordinates.delete()
                    dates = Date.objects.filter(user=user, publication=publication)
                    dates.delete()
                    xcountries = XCountry.objects.filter(user=user, publication=publication)
                    xcountries.delete()

        # If this user has not assessed this publication, or if this assessment was just deleted, above
        if not assessments.filter(publication=publication).exists():

            # Copy this assessment.
            assessment = deepcopy(assessment_to_copy)
            assessment.pk = None  # By setting pk to None, a new instance will be created when this is saved.
            assessment.user = user
            assessment.save()
            if publication_pk not in completed_assessments:
                completed_assessments.append(publication_pk)
                assessment_status.completed_assessments = completed_assessments
                assessment_status.save()

            # Copy experiments for this publication.
            experiments = Experiment.objects.filter(user=user_to_copy, publication=publication)
            for experiment_to_copy in experiments:
                experiment = deepcopy(experiment_to_copy)
                experiment.pk = None
                experiment.user = user
                experiment.save()
                # Copy coordinates for this experiment.
                coordinates = Coordinates.objects.filter(experiment=experiment_to_copy)
                for coordinate in coordinates:
                    coordinate = deepcopy(coordinate)
                    coordinate.pk = None
                    coordinate.user = user
                    coordinate.experiment = experiment
                    coordinate.experiment_index = experiment
                    coordinate.save()
                # Copy countries for this experiment.
                xcountries = XCountry.objects.filter(experiment=experiment_to_copy)
                for xcountry in xcountries:
                    xcountry = deepcopy(xcountry)
                    xcountry.pk = None
                    xcountry.user = user
                    xcountry.experiment = experiment
                    xcountry.experiment_index = experiment
                    xcountry.save()
                # Copy dates for this experiment.
                dates = Date.objects.filter(experiment=experiment_to_copy)
                for date in dates:
                    date = deepcopy(date)
                    date.pk = None
                    date.user = user
                    date.experiment = experiment
                    date.experiment_index = experiment
                    date.save()
                # Copy study for this experiment.
                studies = Study.objects.filter(experiment=experiment_to_copy)
                for study in studies:
                    study = deepcopy(study)
                    study.pk = None
                    study.user = user
                    study.experiment = experiment
                    study.experiment_index = experiment
                    study.save()
                # Copy experiment_designs for this experiment.
                experiment_designs = ExperimentDesign.objects.filter(experiment=experiment_to_copy)
                for experiment_design in experiment_designs:
                    experiment_design = deepcopy(experiment_design)
                    experiment_design.pk = None
                    experiment_design.experiment = experiment
                    experiment_design.save()
                # Copy experiment_populations for this experiment.
                experiment_populations = ExperimentPopulation.objects.filter(experiment=experiment_to_copy)
                for experiment_population_to_copy in experiment_populations:
                    experiment_population = deepcopy(experiment_population_to_copy)
                    experiment_population.pk = None
                    experiment_population.experiment = experiment
                    experiment_population.save()
                    # Copy coordinates for this experiment_population.
                    coordinates = Coordinates.objects.filter(population=experiment_population_to_copy)
                    for coordinate in coordinates:
                        coordinate = deepcopy(coordinate)
                        coordinate.pk = None
                        coordinate.user = user
                        coordinate.population = experiment_population
                        coordinate.population_index = experiment_population
                        coordinate.experiment_index = experiment
                        coordinate.save()
                    # Copy countries for this experiment_population.
                    xcountries = XCountry.objects.filter(population=experiment_population_to_copy)
                    for xcountry in xcountries:
                        xcountry = deepcopy(xcountry)
                        xcountry.pk = None
                        xcountry.user = user
                        xcountry.population = experiment_population
                        xcountry.population_index = experiment_population
                        xcountry.experiment_index = experiment
                        xcountry.save()
                    # Copy dates for this experiment_population.
                    dates = Date.objects.filter(population=experiment_population_to_copy)
                    for date in dates:
                        date = deepcopy(date)
                        date.pk = None
                        date.user = user
                        date.population = experiment_population
                        date.population_index = experiment_population
                        date.experiment_index = experiment
                        date.save()
                    # Copy study for this experiment_population.
                    studies = Study.objects.filter(population=experiment_population_to_copy)
                    for study in studies:
                        study = deepcopy(study)
                        study.pk = None
                        study.user = user
                        study.population = experiment_population
                        study.population_index = experiment_population
                        study.experiment_index = experiment
                        study.save()
                    # Copy experiment_population_outcomes for this experiment_population.
                    experiment_population_outcomes = ExperimentPopulationOutcome.objects.filter(experiment_population=experiment_population_to_copy)
                    for experiment_population_outcome_to_copy in experiment_population_outcomes:
                        experiment_population_outcome = deepcopy(experiment_population_outcome_to_copy)
                        experiment_population_outcome.pk = None
                        experiment_population_outcome.experiment_population = experiment_population
                        experiment_population_outcome.save()

            # Copy other publication-level metadata for this publication.
            # Copy coordinates for this publication.
            coordinates = Coordinates.objects.filter(publication=publication, user=user_to_copy)
            for coordinate in coordinates:
                coordinate = deepcopy(coordinate)
                coordinate.pk = None
                coordinate.user = user
                coordinate.save()
            # Copy countries for this publication.
            xcountries = XCountry.objects.filter(publication=publication, user=user_to_copy)
            for xcountry in xcountries:
                xcountry = deepcopy(xcountry)
                xcountry.pk = None
                xcountry.user = user
                xcountry.save()
            # Copy dates for this publication.
            # There should only be one set of start and end dates, so do not
            # copy if it already exists. If merge_or_overwrite == "overwrite",
            # it will already have been deleted, above.
            if not Date.objects.filter(publication=publication, user=user).exists():
                dates = Date.objects.filter(publication=publication, user=user_to_copy)
                for date in dates:
                    date = deepcopy(date)
                    date.pk = None
                    date.user = user
                    date.save()

            # Copy publication_populations for this publication.
            publication_populations = PublicationPopulation.objects.filter(user=user_to_copy, publication=publication)
            for publication_population_to_copy in publication_populations:
                publication_population = deepcopy(publication_population_to_copy)
                publication_population.pk = None
                publication_population.user = user
                publication_population.save()
                # Copy publication_population_outcomes for this publication_population.
                publication_population_outcomes = PublicationPopulationOutcome.objects.filter(publication_population=publication_population_to_copy)
                for publication_population_outcome_to_copy in publication_population_outcomes:
                    publication_population_outcome = deepcopy(publication_population_outcome_to_copy)
                    publication_population_outcome.pk = None
                    publication_population_outcome.user = user
                    publication_population_outcome.publication_population = publication_population
                    publication_population_outcome.save()

finish_time = datetime.now().time()
print("Start time: ", start_time)
print("Finish time: ", finish_time)

#TODO: copy EAVs
