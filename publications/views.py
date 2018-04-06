from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
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
from .forms import PublicationForm, AssessmentForm, ExperimentForm, ExperimentCropForm, ExperimentDesignForm, ExperimentLatLongForm, ExperimentPopulationForm, ExperimentPopulationOutcomeForm, EffectForm, SignUpForm
from .models import Assessment, Crop, Experiment, Intervention, Outcome, Population, ExperimentCrop, ExperimentDesign, ExperimentLatLong, ExperimentPopulation, ExperimentPopulationOutcome, Publication, Subject, User
from mptt.forms import TreeNodeChoiceField












from haystack.generic_views import SearchView
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet

class MySearchView(SearchView):
    template_name = 'search/search.html'

    def get_queryset(self, *args, **kwargs):
        subject = self.kwargs['subject']
        subject = Subject.objects.get(slug=subject)
        queryset = super(MySearchView, self).get_queryset()
        return queryset.filter(subject=subject)

    def get_context_data(self, *args, **kwargs):
        context = super(MySearchView, self).get_context_data(*args, **kwargs)
        # do something
        return context











def subject(request, subject):
    subject = Subject.objects.get(slug=subject)
    context = {'subject': subject}
    return render(request, 'publications/subject.html', context)


def publications(request, subject):
    subject = Subject.objects.get(slug=subject)
    publications = Publication.objects.filter(subject=subject).order_by('title')
    page = request.GET.get('page', 1)
    paginator = Paginator(publications, 10)
    try:
        publications = paginator.page(page)
    except PageNotAnInteger:
        publications = paginator.page(1)
    except EmptyPage:
        publications = paginator.page(paginator.num_pages)
    context = {
        'subject': subject,
        'publications': publications
    }
    return render(request, 'publications/publications.html', context)


def home(request):
    return render(request, 'publications/home.html')


def about(request):
    return render(request, 'publications/about.html')


def methods(request):
    return render(request, 'publications/methods.html')


def contact(request):
    return render(request, 'publications/contact.html')


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

@login_required
def publication(request, subject, publication_pk):
    """
    On this page, the user chooses interventions for this publication.
    """
    user = request.user
    data = request.POST or None
    subject = Subject.objects.get(slug=subject)
    ExperimentFormSet = modelformset_factory(Experiment, form=ExperimentForm, extra=2, can_delete=True)
    # This publication
    publication = Publication.objects.get(pk=publication_pk)
    # Form for this publication
    publication_form = PublicationForm(data=data, instance=publication, prefix="publication_form")
    # Form for this assessment
    if Assessment.objects.filter(publication=publication, user=user, subject=subject).exists():
        assessment = Assessment.objects.get(publication=publication, user=user, subject=subject)
        assessment_form = AssessmentForm(data=data, instance=assessment, prefix="assessment_form")
    else:
        assessment_form = AssessmentForm(data=data, prefix="assessment_form")
    # Formset for this publication
    formset = ExperimentFormSet(data=data, queryset=Experiment.objects.filter(publication=publication), prefix="experiment_formset")
    # Intervention choices for the formset
    for form in formset:
        form.fields['intervention'] = TreeNodeChoiceField(queryset=Intervention.objects.all().get_descendants(include_self=True), level_indicator = "---")
    if request.method == 'POST':
        with transaction.atomic():
            if publication_form.is_valid():
                publication = publication_form.save()
            if assessment_form.is_valid():
                assessment = assessment_form.save(commit=False)
                assessment.user = user
                assessment.publication = publication
                assessment.subject = subject
                assessment.save()
            if formset.is_valid():
                instances = formset.save(commit=False)
                if 'delete' in request.POST:
                    for obj in formset.deleted_objects:
                        obj.delete()
                else:
                    for instance in instances:
                        instance.publication = publication
                        instance.user = user
                        instance.save()
            return redirect('publication', subject=subject, publication_pk=publication_pk)
    context = {
        'subject': subject,
        'publication': publication,
        'publication_form': publication_form,
        'assessment_form': assessment_form,
        'experiment_formset': formset
    }
    return render(request, 'publications/publication.html', context)


@login_required
def experiment(request, subject, publication_pk, experiment_index):
    """
    On this page, the user chooses populations, experimental designs, crops, IUCN actions, IUCN threats, and coordinates for this intervention (AKA "experiment").
    """
    data = request.POST or None
    subject = Subject.objects.get(slug=subject)
    ExperimentCropFormSet = modelformset_factory(ExperimentCrop, form=ExperimentCropForm, extra=2, can_delete=True)
    ExperimentDesignFormSet = modelformset_factory(ExperimentDesign, form=ExperimentDesignForm, extra=3, can_delete=True)
    ExperimentLatLongFormSet = modelformset_factory(ExperimentLatLong, form=ExperimentLatLongForm, extra=2, can_delete=True)
    ExperimentPopulationFormSet = modelformset_factory(ExperimentPopulation, form=ExperimentPopulationForm, extra=2, can_delete=True)
    # This publication
    publication = Publication.objects.get(pk=publication_pk)
    # This experiment
    experiments = Experiment.objects.filter(publication=publication).order_by('pk')
    experiment = experiments[experiment_index]
    # Formsets for this experiment
    experiment_population_formset = ExperimentPopulationFormSet(data=data, queryset=ExperimentPopulation.objects.filter(experiment=experiment), prefix="experiment_population_formset")
    experiment_crop_formset = ExperimentCropFormSet(data=data, queryset=ExperimentCrop.objects.filter(experiment=experiment), prefix="experiment_crop_formset")
    # Crop choices for the formset
    for form in experiment_crop_formset:
        form.fields['crop'] = TreeNodeChoiceField(queryset=Crop.objects.all().get_descendants(include_self=True), level_indicator = "---")
    experiment_design_formset = ExperimentDesignFormSet(data=data, queryset=ExperimentDesign.objects.filter(experiment=experiment), prefix="experiment_design_formset")
    experiment_lat_long_formset = ExperimentLatLongFormSet(data=data, queryset=ExperimentLatLong.objects.filter(experiment=experiment), prefix="experiment_lat_long_formset")
    if request.method == 'POST':
        with transaction.atomic():
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
            return redirect('experiment', subject=subject, publication_pk=publication_pk, experiment_index=experiment_index)
    context = {
        'subject': subject,
        'publication': publication,
        'experiment': experiment,
        'experiment_index': experiment_index,
        'experiment_crop_formset': experiment_crop_formset,
        'experiment_design_formset': experiment_design_formset,
        'experiment_lat_long_formset': experiment_lat_long_formset,
        'experiment_population_formset': experiment_population_formset
    }
    return render(request, 'publications/experiment.html', context)


@login_required
def population(request, subject, publication_pk, experiment_index, population_index):
    """
    On this page, the user chooses populations for this intervention (AKA "experiment").
    """
    data = request.POST or None
    subject = Subject.objects.get(slug=subject)
    ExperimentPopulationOutcomeFormSet = modelformset_factory(ExperimentPopulationOutcome, form=ExperimentPopulationOutcomeForm, extra=2, can_delete=True)
    # This publication
    publication = Publication.objects.get(pk=publication_pk)
    experiments = Experiment.objects.filter(publication=publication).order_by('pk')
    # This experiment
    experiment = experiments[experiment_index]
    experiment_populations = ExperimentPopulation.objects.filter(experiment=experiment).order_by('pk')
    # This population
    experiment_population = experiment_populations[population_index]
    # Formset for this population
    formset = ExperimentPopulationOutcomeFormSet(data=data, queryset=ExperimentPopulationOutcome.objects.filter(experiment_population=experiment_population), prefix="experiment_population_outcome_formset")
    # Outcome choices for the formset
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
            return redirect('population', subject=subject, publication_pk=publication_pk, experiment_index=experiment_index, population_index=population_index)
    context = {
        'subject': subject,
        'publication': publication,
        'experiment': experiment,
        'experiment_population': experiment_population,
        'experiment_index': experiment_index,
        'population_index': population_index,
        'experiment_population_outcome_formset': formset
    }
    return render(request, 'publications/population.html', context)


@login_required
def outcome(request, subject, publication_pk, experiment_index, population_index, outcome_index):
    """
    On this page, the user chooses outcomes for this population.
    """
    data = request.POST or None
    subject = Subject.objects.get(slug=subject)
    EffectFormSet = modelformset_factory(ExperimentPopulationOutcome, form=EffectForm, extra=0, can_delete=True)
    # This publication
    publication = Publication.objects.get(pk=publication_pk)
    # This experiment
    experiments = Experiment.objects.filter(publication=publication).order_by('pk')
    experiment = experiments[experiment_index]
    # This population
    experiment_populations = ExperimentPopulation.objects.filter(experiment=experiment).order_by('pk')
    experiment_population = experiment_populations[population_index]
    # This outcome
    experiment_population_outcomes = ExperimentPopulationOutcome.objects.filter(experiment_population=experiment_population).order_by('pk')
    experiment_population_outcome = experiment_population_outcomes[outcome_index]
    # Formset for this outcome
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
            return redirect('outcome', subject=subject, publication_pk=publication_pk, experiment_index=experiment_index, population_index=population_index, outcome_index=outcome_index)
    context = {
        'subject': subject,
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


def browse_publications_by_intervention(request, subject):
    subject = Subject.objects.get(slug=subject)
    context = {
        'subject': subject,  # Browse within this subject
        'interventions': Intervention.objects.all(),
    }
    return render(request, 'publications/browse_publications_by_intervention.html', context)


def browse_publications_by_outcome(request, subject):
    subject = Subject.objects.get(slug=subject)
    context = {
        'subject': subject,  # Browse within this subject
        'outcomes': Outcome.objects.all(),
    }
    return render(request, 'publications/browse_publications_by_outcome.html', context)


def publications_by_intervention(request, subject, path, instance):
    subject = Subject.objects.get(slug=subject)
    interventions = instance.get_descendants(include_self=True)
    experiments = Experiment.objects.filter(intervention__in=interventions)
    publications = Publication.objects.filter(subject=subject, experiment__in=experiments).order_by('title')
    context = {
        'subject': subject,
        'publications': publications
    }
    return render(request, 'publications/publications.html', context)


def publications_by_outcome(request, subject, path, instance):
    subject = Subject.objects.get(slug=subject)
    outcomes = instance.get_descendants(include_self=True)
    experiment_population_outcomes = ExperimentPopulationOutcome.objects.filter(outcome__in=outcomes)
    experiment_populations = ExperimentPopulation.objects.filter(experimentpopulationoutcome__in=experiment_population_outcomes)
    experiments = Experiment.objects.filter(experimentpopulation__in=experiment_populations)
    publications = Publication.objects.filter(subject=subject, experiment__in=experiments).order_by('title')
    context = {
        'subject': subject,
        'publications': publications
    }
    return render(request, 'publications/publications.html', context)
