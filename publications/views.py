from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from .forms import PublicationForm, ExperimentForm, ExperimentCropForm, ExperimentDesignForm, ExperimentIUCNThreatForm, ExperimentLatLongForm, ExperimentPopulationForm, ExperimentPopulationOutcomeForm, EffectForm
from .models import Publication, Experiment, Population, Crop, ExperimentCrop, ExperimentDesign, ExperimentIUCNThreat, ExperimentLatLong, ExperimentPopulation, ExperimentPopulationOutcome



from .models import Outcome
from mptt.forms import TreeNodeChoiceField




def home(request):
    publications = Publication.objects.all().order_by('title')
    page = request.GET.get('page', 1)
    paginator = Paginator(publications, 10)
    try:
        publications = paginator.page(page)
    except PageNotAnInteger:
        publications = paginator.page(1)
    except EmptyPage:
        publications = paginator.page(paginator.num_pages)
    context = {
        'publications': publications
    }
    return render(request, 'publications/home.html', context)


def add_publication(request):
    if request.method == 'POST':
        publication_form = PublicationForm(request.POST, prefix="publication_form")
        publication = publication_form.save()
        return redirect('home')
    else:
        publication_form = PublicationForm(prefix="publication_form")

    context = {
        'publication_form': publication_form
    }

    return render(request, 'publications/publication.html', context)


def publication(request, publication_pk):
    publication = Publication.objects.get(pk=publication_pk)
    ExperimentFormSet = modelformset_factory(Experiment, form=ExperimentForm, extra=2, can_delete=True)
    if request.method == 'POST':
        publication_form = PublicationForm(request.POST, instance=publication, prefix="publication_form")
        experiment_formset = ExperimentFormSet(request.POST, prefix="experiment_formset")
        with transaction.atomic():
            if publication_form.is_valid():
                publication = publication_form.save()
            formset = experiment_formset
            if formset.is_valid():
                instances = formset.save(commit=False)
                if 'delete' in request.POST:
                    for obj in formset.deleted_objects:
                        obj.delete()
                else:
                    for instance in instances:
                        instance.publication = publication
                        instance.save()
            return redirect('publication', publication_pk=publication_pk)
    else:
        publication_form = PublicationForm(instance=publication, prefix="publication_form")
        if Experiment.objects.filter(publication=publication).exists():
            experiments = Experiment.objects.filter(publication=publication).order_by('pk')
            experiment_formset = ExperimentFormSet(queryset=experiments, prefix="experiment_formset")
        else:
            experiment_formset = ExperimentFormSet(queryset=Experiment.objects.none(), prefix="experiment_formset")
            experiments = []

    context = {
        'publication': publication,
        'experiments': experiments,
        'publication_form': publication_form,
        'experiment_formset': experiment_formset
    }

    return render(request, 'publications/publication.html', context)


def experiment(request, publication_pk, experiment_index):
    publication = Publication.objects.get(pk=publication_pk)
    experiments = Experiment.objects.filter(publication=publication).order_by('pk')
    experiment = experiments[experiment_index]
    ExperimentCropFormSet = modelformset_factory(ExperimentCrop, form=ExperimentCropForm, extra=2, can_delete=True)
    ExperimentDesignFormSet = modelformset_factory(ExperimentDesign, form=ExperimentDesignForm, extra=3, can_delete=True)
    ExperimentIUCNThreatFormSet = modelformset_factory(ExperimentIUCNThreat, form=ExperimentIUCNThreatForm, extra=2, can_delete=True)
    ExperimentLatLongFormSet = modelformset_factory(ExperimentLatLong, form=ExperimentLatLongForm, extra=2, can_delete=True)
    ExperimentPopulationFormSet = modelformset_factory(ExperimentPopulation, form=ExperimentPopulationForm, extra=2, can_delete=True)
    if request.method == 'POST':
        experiment_population_formset = ExperimentPopulationFormSet(request.POST, prefix="experiment_population_formset")
        experiment_crop_formset = ExperimentCropFormSet(request.POST, prefix="experiment_crop_formset")
        experiment_design_formset = ExperimentDesignFormSet(request.POST, prefix="experiment_design_formset")
        experiment_IUCN_threat_formset = ExperimentIUCNThreatFormSet(request.POST, prefix="experiment_IUCN_threat_formset")
        experiment_lat_long_formset = ExperimentLatLongFormSet(request.POST, prefix="experiment_lat_long_formset")
        with transaction.atomic():
            #TODO: Do this in a loop:
            formset = experiment_population_formset
            if formset.is_valid():
                instances = formset.save(commit=False)
                if 'delete' in request.POST:
                    for obj in formset.deleted_objects:
                        obj.delete()
                else:
                    for instance in instances:
                        instance.experiment = experiment
                        if instance.old_population is not None:
                        # If the user changes the population, then we need to delete the instances of ExperimentPopulationOutcome that depend on the old population.
                            if (instance.old_population != instance.population):
                                ExperimentPopulationOutcome.objects.filter(experiment_population=instance).delete()
                        instance.old_population = instance.population
                        instance.save()
            formset = experiment_crop_formset
            if formset.is_valid():
                instances = formset.save(commit=False)
                if 'delete' in request.POST:
                    for obj in formset.deleted_objects:
                        obj.delete()
                else:
                    for instance in instances:
                        instance.experiment = experiment
                        instance.save()
            formset = experiment_design_formset
            if formset.is_valid():
                instances = formset.save(commit=False)
                if 'delete' in request.POST:
                    for obj in formset.deleted_objects:
                        obj.delete()
                else:
                    for instance in instances:
                        instance.experiment = experiment
                        instance.save()
            formset = experiment_IUCN_threat_formset
            if formset.is_valid():
                instances = formset.save(commit=False)
                if 'delete' in request.POST:
                    for obj in formset.deleted_objects:
                        obj.delete()
                else:
                    for instance in instances:
                        instance.experiment = experiment
                        instance.save()
            formset = experiment_lat_long_formset
            if formset.is_valid():
                instances = formset.save(commit=False)
                if 'delete' in request.POST:
                    for obj in formset.deleted_objects:
                        obj.delete()
                else:
                    for instance in instances:
                        instance.experiment = experiment
                        instance.save()
            return redirect('experiment', publication_pk=publication_pk, experiment_index=experiment_index)
    else:
        if ExperimentCrop.objects.filter(experiment=experiment).exists():
            experiment_crop_formset = ExperimentCropFormSet(queryset=ExperimentCrop.objects.filter(experiment=experiment), prefix="experiment_crop_formset")
        else:
            experiment_crop_formset = ExperimentCropFormSet(queryset=ExperimentCrop.objects.none(), initial=[{'crop': Crop.objects.get(crop='Cassava')}], prefix="experiment_crop_formset")

        if ExperimentDesign.objects.filter(experiment=experiment).exists():
            experiment_design_formset = ExperimentDesignFormSet(queryset=ExperimentDesign.objects.filter(experiment=experiment), prefix="experiment_design_formset")
        else:
            experiment_design_formset = ExperimentDesignFormSet(queryset=ExperimentDesign.objects.none(), prefix="experiment_design_formset")

        if ExperimentIUCNThreat.objects.filter(experiment=experiment).exists():
            experiment_IUCN_threat_formset = ExperimentIUCNThreatFormSet(queryset=ExperimentIUCNThreat.objects.filter(experiment=experiment), prefix="experiment_IUCN_threat_formset")
        else:
            experiment_IUCN_threat_formset = ExperimentIUCNThreatFormSet(queryset=ExperimentIUCNThreat.objects.none(), prefix="experiment_IUCN_threat_formset")

        if ExperimentLatLong.objects.filter(experiment=experiment).exists():
            experiment_lat_long_formset = ExperimentLatLongFormSet(queryset=ExperimentLatLong.objects.filter(experiment=experiment), prefix="experiment_lat_long_formset")
        else:
            experiment_lat_long_formset = ExperimentLatLongFormSet(queryset=ExperimentLatLong.objects.none(), prefix="experiment_lat_long_formset")

        if ExperimentPopulation.objects.filter(experiment=experiment).exists():
            experiment_population_formset = ExperimentPopulationFormSet(queryset=ExperimentPopulation.objects.filter(experiment=experiment).order_by('pk'), prefix="experiment_population_formset")
        else:
            experiment_population_formset = ExperimentPopulationFormSet(queryset=ExperimentPopulation.objects.none(), prefix="experiment_population_formset")

    context = {
        'publication': publication,
        'experiment': experiment,
        'experiment_index': experiment_index,
        'experiment_crop_formset': experiment_crop_formset,
        'experiment_design_formset': experiment_design_formset,
        'experiment_IUCN_threat_formset': experiment_IUCN_threat_formset,
        'experiment_lat_long_formset': experiment_lat_long_formset,
        'experiment_population_formset': experiment_population_formset
    }

    return render(request, 'publications/experiment.html', context)


def population(request, publication_pk, experiment_index, population_index):
    publication = Publication.objects.get(pk=publication_pk)
    experiments = Experiment.objects.filter(publication=publication).order_by('pk')
    experiment = experiments[experiment_index]
    experiment_populations = ExperimentPopulation.objects.filter(experiment=experiment).order_by('pk')
    experiment_population = experiment_populations[population_index]
    ExperimentPopulationOutcomeFormSet = modelformset_factory(ExperimentPopulationOutcome, form=ExperimentPopulationOutcomeForm, extra=2, can_delete=True)
    data = request.POST or None




    #TODO: Simplify all formsets in views like this:




    formset = ExperimentPopulationOutcomeFormSet(data=data, queryset=ExperimentPopulationOutcome.objects.filter(experiment_population=experiment_population), prefix="experiment_population_outcome_formset")
    for form in formset:
        form.fields['outcome'] = TreeNodeChoiceField(queryset=Outcome.objects.get(outcome=experiment_population.population).get_descendants(include_self=True), level_indicator = "->")

    if request.method == 'POST':
        with transaction.atomic():
            if formset.is_valid():
                instances = formset.save(commit=False)
                if 'delete' in request.POST:
                    for obj in formset.deleted_objects:
                        obj.delete()
                else:
                    for instance in instances:
                        instance.experiment_population = experiment_population
                        instance.save()
            return redirect('population', publication_pk=publication_pk, experiment_index=experiment_index, population_index=population_index)

    context = {
        'publication': publication,
        'experiment': experiment,
        'experiment_population': experiment_population,
        'experiment_index': experiment_index,
        'population_index': population_index,
        'experiment_population_outcome_formset': formset
    }

    return render(request, 'publications/population.html', context)


def outcome(request, publication_pk, experiment_index, population_index, outcome_index):
    publication = Publication.objects.get(pk=publication_pk)
    experiments = Experiment.objects.filter(publication=publication).order_by('pk')
    experiment = experiments[experiment_index]
    experiment_populations = ExperimentPopulation.objects.filter(experiment=experiment).order_by('pk')
    experiment_population = experiment_populations[population_index]
    experiment_population_outcomes = ExperimentPopulationOutcome.objects.filter(experiment_population=experiment_population).order_by('pk')
    experiment_population_outcome = experiment_population_outcomes[outcome_index]
    EffectFormSet = modelformset_factory(ExperimentPopulationOutcome, form=EffectForm, extra=0, can_delete=True)
    if request.method == 'POST':
        formset = EffectFormSet(request.POST, prefix="effect_formset")
        with transaction.atomic():
            if formset.is_valid():
                instances = formset.save(commit=False)
                if 'delete' in request.POST:
                    for obj in formset.deleted_objects:
                        obj.delete()
                else:
                    for instance in instances:
                        instance.experiment_population = experiment_population
                        instance.save()
            return redirect('outcome', publication_pk=publication_pk, experiment_index=experiment_index, population_index=population_index, outcome_index=outcome_index)
    else:
        if ExperimentPopulationOutcome.objects.filter(pk=experiment_population_outcome.pk).exists():
            effect_formset = EffectFormSet(queryset=ExperimentPopulationOutcome.objects.filter(pk=experiment_population_outcome.pk), prefix="effect_formset")
        else:
            effect_formset = EffectFormSet(queryset=ExperimentPopulationOutcome.objects.none(), prefix="effect_formset")

    context = {
        'publication': publication,
        'experiment': experiment,
        'experiment_population': experiment_population,
        'experiment_population_outcome': experiment_population_outcome,
        'experiment_index': experiment_index,
        'population_index': population_index,
        'outcome_index': outcome_index,
        'effect_formset': effect_formset
    }

    return render(request, 'publications/outcome.html', context)
