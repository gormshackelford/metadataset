from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.template import loader
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from .forms import PublicationForm, ExperimentForm, ExperimentCropForm, ExperimentDesignForm, ExperimentIUCNThreatForm, ExperimentLatLongForm, ExperimentPopulationForm, ExperimentPopulationOutcomeForm, EffectForm, SignUpForm
from .models import Publication, Experiment, Population, Crop, ExperimentCrop, ExperimentDesign, ExperimentIUCNThreat, ExperimentLatLong, ExperimentPopulation, ExperimentPopulationOutcome, Intervention, User



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


def about(request):
    context = {
        'nodes': Intervention.objects.all()
    }
    return render(request, 'publications/about.html', context)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():

            """
            ''' Begin reCAPTCHA validation '''

            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': config.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req =  urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())

            ''' End reCAPTCHA validation '''
            """

#            if result['success']:
            user = form.save()
            user.refresh_from_db()  # Load the profile instance created by the signal.
            user.profile.institution = form.cleaned_data.get('institution')
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'MetaDataSet'
            message = render_to_string('publications/confirm_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('email_sent')
    else:
        form = SignUpForm()
    return render(request, 'publications/signup.html', {'form': form})


def email_sent(request):
    return render(request, 'publications/email_sent.html')


def email_confirmed(request):
    return render(request, 'publications/email_confirmed.html')


def email_not_confirmed(request):
    return render(request, 'publications/email_not_confirmed.html')


def confirm_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_is_confirmed = True
        user.save()
        login(request, user)
        return render(request, 'publications/email_confirmed.html')
    else:
        return render(request, 'publications/email_not_confirmed.html', {'uid': uid})


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
    data = request.POST or None
    publication_form = PublicationForm(data=data, instance=publication, prefix="publication_form")
    formset = ExperimentFormSet(data=data, prefix="experiment_formset")
    for form in formset:
        form.fields['intervention'] = TreeNodeChoiceField(queryset=Intervention.objects.all().get_descendants(include_self=True), level_indicator = "---")
    if request.method == 'POST':
        with transaction.atomic():
            if publication_form.is_valid():
                publication = publication_form.save()
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

    context = {
        'publication': publication,
        'publication_form': publication_form,
        'experiment_formset': formset
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




    #TODO: Simplify formsets in experiment view like this:


    data = request.POST or None


    formset = ExperimentPopulationOutcomeFormSet(data=data, queryset=ExperimentPopulationOutcome.objects.filter(experiment_population=experiment_population), prefix="experiment_population_outcome_formset")
    for form in formset:
        form.fields['outcome'] = TreeNodeChoiceField(queryset=Outcome.objects.get(outcome=experiment_population.population).get_descendants(include_self=True), level_indicator = "---")
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
    data = request.POST or None
    formset = EffectFormSet(data=data, queryset=ExperimentPopulationOutcome.objects.filter(pk=experiment_population_outcome.pk), prefix="effect_formset")
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
            return redirect('outcome', publication_pk=publication_pk, experiment_index=experiment_index, population_index=population_index, outcome_index=outcome_index)

    context = {
        'publication': publication,
        'experiment': experiment,
        'experiment_population': experiment_population,
        'experiment_population_outcome': experiment_population_outcome,
        'experiment_index': experiment_index,
        'population_index': population_index,
        'outcome_index': outcome_index,
        'effect_formset': formset
    }

    return render(request, 'publications/outcome.html', context)
