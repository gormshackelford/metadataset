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
from ast import literal_eval
from random import shuffle
from .tokens import account_activation_token
from .forms import PublicationForm, AssessmentForm, EffectForm, ExperimentForm, ExperimentCountryForm, ExperimentCropForm, ExperimentDateForm, ExperimentDesignForm, ExperimentLatLongForm, ExperimentPopulationForm, ExperimentPopulationOutcomeForm, FullTextAssessmentForm, ProfileForm, SignUpForm, UserForm
from .models import Assessment, AssessmentStatus, Crop, Experiment, Intervention, Outcome, Population, ExperimentCountry, ExperimentCrop, ExperimentDate, ExperimentDesign, ExperimentLatLong, ExperimentPopulation, ExperimentPopulationOutcome, Publication, Subject, User
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
    user = request.user
    subject = Subject.objects.get(slug=subject)
    context = {
        'subject': subject
    }
    # Get data for the sidebar.
    if user.is_authenticated:
        status = get_status(user, subject)
        context.update(status)
    return render(request, 'publications/subject.html', context)


def publications(request, subject, state='all'):
    user = request.user
    subject = Subject.objects.get(slug=subject)
    # All publications
    if (state == 'all'):
        publications = Publication.objects.filter(subject=subject).order_by('title')
    # Publications that this user has assessed as relevant based on title/abstract
    elif (state == 'relevant'):
        publications = Publication.objects.distinct().filter(
            assessment__in=Assessment.objects.filter(
                subject=subject,
                user=user,
                is_relevant=True
            )
        ).order_by('title')
    # Publications that this user has assessed as not relevant based on title/abstract
    elif (state == 'not_relevant'):
        publications = Publication.objects.distinct().filter(
            assessment__in=Assessment.objects.filter(
                subject=subject,
                user=user,
                is_relevant=False
            )
        ).order_by('title')
    # Publications that this user has not yet assessed based on title/abstract
    elif (state == 'not_assessed'):
        publications = Publication.objects.distinct().exclude(
            assessment__in=Assessment.objects.filter(
                subject=subject,
                user=user
            )
        ).order_by('title')
    # Publications that this user has assessed as relevant based on full text
    elif (state == 'relevant_full_texts'):
        publications = Publication.objects.distinct().filter(
            assessment__in=Assessment.objects.filter(
                subject=subject,
                user=user,
                is_relevant=True,  # is_relevant based on title/abstract
                full_text_is_relevant=True
            )
        ).order_by('title')
    # Publications that this user has assessed as not relevant based on full text
    elif (state == 'not_relevant_full_texts'):
        publications = Publication.objects.distinct().filter(
            assessment__in=Assessment.objects.filter(
                subject=subject,
                user=user,
                is_relevant=True,  # is_relevant based on title/abstract
                full_text_is_relevant=False
            )
        ).order_by('title')
    # Publications that this user has not yet assessed based on full text
    elif (state == 'not_assessed_full_texts'):
        publications = Publication.objects.distinct().filter(
            assessment__in=Assessment.objects.filter(
                subject=subject,
                user=user,
                is_relevant=True,  # is_relevant based on title/abstract
                full_text_is_relevant=None
            )
        ).order_by('title')
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
    if user.is_authenticated:
        status = get_status(user, subject)
        context.update(status)
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
@transaction.atomic
def profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.first_name = user_form.cleaned_data.get('first_name')
            user.last_name = user_form.cleaned_data.get('last_name')
            user.profile.institution = profile_form.cleaned_data.get('institution')
            user.save()
            return render(request, 'publications/profile_updated.html')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'publications/profile.html', context)


@login_required
def publication(request, subject, publication_pk):
    """
    On this page, the user chooses interventions for this publication.
    """
    user = request.user
    data = request.POST or None
    subject = Subject.objects.get(slug=subject)
    publication_pk = int(publication_pk)

    # Get data for the sidebar.
    status = get_status(user, subject)
    item = status.get('item')  # item = AssessmentStatus instance for this user and subject
    assessment_order = literal_eval(item.assessment_order)
    completed_assessments = literal_eval(item.completed_assessments)
    completed_full_text_assessments = literal_eval(item.completed_full_text_assessments)
    relevant_publications = literal_eval(item.relevant_publications)

    # The next pk and previous pk in assessment_order, to be used for navigation
    previous_pk = assessment_order[assessment_order.index(publication_pk) - 1]
    try:
        next_pk = assessment_order[assessment_order.index(publication_pk) + 1]
    except:
        next_pk = assessment_order[0]

    ExperimentFormSet = modelformset_factory(Experiment, form=ExperimentForm, extra=2, can_delete=True)
    # This publication
    publication = Publication.objects.get(pk=publication_pk)
    # Form for this assessment
    if Assessment.objects.filter(publication=publication, user=user, subject=subject).exists():
        assessment = Assessment.objects.get(publication=publication, user=user, subject=subject)
        assessment_form = AssessmentForm(data=data, instance=assessment, prefix="assessment_form")
        full_text_assessment_form = FullTextAssessmentForm(data=data, instance=assessment, prefix="full_text_assessment_form")
        # Get relevance for context.
        if assessment.is_relevant == True:
            is_relevant = 'True'
        else:
            is_relevant = 'False'
        if assessment.full_text_is_relevant == True:
            full_text_is_relevant = 'True'
        elif assessment.full_text_is_relevant == False:
            full_text_is_relevant = 'False'
        else:
            full_text_is_relevant = ''  # Not yet assessed
    else:
        assessment_form = AssessmentForm(data=data, prefix="assessment_form")
        full_text_assessment_form = FullTextAssessmentForm(data=data, prefix="full_text_assessment_form")
        is_relevant = ''  # Not yet assessed
        full_text_is_relevant = ''  # Not yet assessed

    # Formset for this publication
    formset = ExperimentFormSet(data=data, queryset=Experiment.objects.filter(publication=publication), prefix="experiment_formset")
    if request.method == 'POST':
        if 'is_relevant' in request.POST:
            with transaction.atomic():
                # Update assessment
                if assessment_form.is_valid():
                    assessment = assessment_form.save(commit=False)
                    assessment.user = user
                    assessment.publication = publication
                    assessment.subject = subject
                    assessment.is_relevant = True
                    assessment.full_text_is_relevant = None
                    assessment.note = ''
                    assessment.save()
                    # Update status and get next assessment
                    if publication_pk not in completed_assessments:
                        completed_assessments.append(publication_pk)
                        item.completed_assessments = completed_assessments
                    if publication_pk not in relevant_publications:
                        relevant_publications.append(publication_pk)
                        item.relevant_publications = relevant_publications
                    next_assessment = get_next_assessment(publication_pk, next_pk, assessment_order, completed_assessments)
                    item.next_assessment = next_assessment
                    if publication_pk in completed_full_text_assessments:
                        completed_full_text_assessments.remove(publication_pk)
                        item.completed_full_text_assessments = completed_full_text_assessments
                    item.save()
                    return redirect('publication', subject=subject, publication_pk=next_assessment)
        if 'is_not_relevant' in request.POST:
            with transaction.atomic():
                if assessment_form.is_valid():
                    # Update assessment
                    assessment = assessment_form.save(commit=False)
                    assessment.user = user
                    assessment.publication = publication
                    assessment.subject = subject
                    assessment.is_relevant = False
                    assessment.full_text_is_relevant = None
                    assessment.note = ''
                    assessment.save()
                    # Update status and get next assessment
                    if publication_pk not in completed_assessments:
                        completed_assessments.append(publication_pk)
                        item.completed_assessments = completed_assessments
                    next_assessment = get_next_assessment(publication_pk, next_pk, assessment_order, completed_assessments)
                    item.next_assessment = next_assessment
                    if publication_pk in relevant_publications:
                        relevant_publications.remove(publication_pk)
                        item.relevant_publications = relevant_publications
                    if publication_pk in completed_full_text_assessments:
                        completed_full_text_assessments.remove(publication_pk)
                        item.completed_full_text_assessments = completed_full_text_assessments
                    item.save()
                    return redirect('publication', subject=subject, publication_pk=next_assessment)
        if 'full_text_is_not_relevant' in request.POST:
            with transaction.atomic():
                if full_text_assessment_form.is_valid():
                    # Update assessments (add the reason for rejection)
                    assessment = full_text_assessment_form.save(commit=False)
                    assessment.user = user
                    assessment.publication = publication
                    assessment.subject = subject
                    assessment.is_relevant = True  # It must be relevant based on the title and abstract if it is to be rejected based on the full text.
                    assessment.full_text_is_relevant = False
                    assessment.save()
                    # Update status and get next assessment
                    if publication_pk not in completed_assessments:
                        completed_assessments.append(publication_pk)
                        item.completed_assessments = completed_assessments
                    if publication_pk not in relevant_publications:
                        relevant_publications.append(publication_pk)
                        item.relevant_publications = relevant_publications
                    next_assessment = get_next_assessment(publication_pk, next_pk, assessment_order, completed_assessments)
                    item.next_assessment = next_assessment
                    if publication_pk not in completed_full_text_assessments:
                        completed_full_text_assessments.append(publication_pk)
                        item.completed_full_text_assessments = completed_full_text_assessments
                    item.save()
                return redirect('publication', subject=subject, publication_pk=publication_pk)
        if 'save' in request.POST or 'delete' in request.POST:
            with transaction.atomic():
                # Before the formset is validated, the choices for the intervention field need to be redefined, or the validation will fail. This is because only a subset of all choices (high level choices in the MPTT tree) were initially shown in the dropdown (for better UI).
                for form in formset:
                    form.fields['intervention'] = TreeNodeChoiceField(queryset=Intervention.objects.all().get_descendants(include_self=True), level_indicator = "---")
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
                    if assessment_form.is_valid():
                        # If interventions have been selected, mark this publication as "relevant" to this systematic review.
                        if Experiment.objects.filter(publication=publication, user=user).exists():
                            # Update assessment
                            assessment = assessment_form.save(commit=False)
                            assessment.user = user
                            assessment.publication = publication
                            assessment.subject = subject
                            assessment.is_relevant = True
                            assessment.full_text_is_relevant = True
                            assessment.note = ''
                            assessment.save()
                            # Update status and get next assessment
                            if publication_pk not in completed_assessments:
                                completed_assessments.append(publication_pk)
                                item.completed_assessments = completed_assessments
                                next_assessment = get_next_assessment(publication_pk, next_pk, assessment_order, completed_assessments)
                                item.next_assessment = next_assessment
                                item.save()
                            if publication_pk not in relevant_publications:
                                relevant_publications.append(publication_pk)
                                item.relevant_publications = relevant_publications
                                item.save()
                            if publication_pk not in completed_full_text_assessments:
                                completed_full_text_assessments.append(publication_pk)
                                item.completed_full_text_assessments = completed_full_text_assessments
                                item.save()
                        # If all interventions have been deleted, remove this publication from the completed assessments.
                        elif 'delete' in request.POST:
                            if publication_pk in completed_assessments:
                                completed_assessments.remove(publication_pk)
                                item.completed_assessments = completed_assessments
                                relevant_publications.remove(publication_pk)
                                item.relevant_publications = relevant_publications
                                next_assessment = publication_pk
                                item.next_assessment = next_assessment
                                item.save()
                            if publication_pk in completed_full_text_assessments:
                                completed_full_text_assessments.remove(publication_pk)
                                item.completed_full_text_assessments = completed_full_text_assessments
                                item.save()
                            if Assessment.objects.filter(publication=publication, user=user).exists():
                                Assessment.objects.filter(publication=publication, user=user).delete()
                return redirect('publication', subject=subject, publication_pk=publication_pk)
    else:
        # Intervention choices for the formset (high-level choices only)
        for form in formset:
            form.fields['intervention'] = TreeNodeChoiceField(required=False, queryset=Intervention.objects.all().get_descendants(include_self=True).filter(level__lte=1), level_indicator = "---")
    context = {
        'subject': subject,
        'publication': publication,
        'assessment_form': assessment_form,
        'full_text_assessment_form': full_text_assessment_form,
        'experiment_formset': formset,
        'is_relevant': is_relevant,
        'full_text_is_relevant': full_text_is_relevant,
        'next_pk': next_pk,
        'previous_pk': previous_pk
    }
    status = get_status(user, subject)
    context.update(status)
    return render(request, 'publications/publication.html', context)


@login_required
def experiment(request, subject, publication_pk, experiment_index):
    """
    On this page, the user chooses populations, experimental designs, crops, countries, and coordinates for this intervention (AKA "experiment").
    """
    user = request.user
    data = request.POST or None
    subject = Subject.objects.get(slug=subject)
    ExperimentFormSet = modelformset_factory(Experiment, form=ExperimentForm, extra=0, can_delete=False)
    ExperimentCountryFormSet = modelformset_factory(ExperimentCountry, form=ExperimentCountryForm, extra=2, can_delete=True)
    ExperimentCropFormSet = modelformset_factory(ExperimentCrop, form=ExperimentCropForm, extra=2, can_delete=True)
    ExperimentDateFormSet = modelformset_factory(ExperimentDate, form=ExperimentDateForm, extra=2, max_num=2, can_delete=True)
    ExperimentDesignFormSet = modelformset_factory(ExperimentDesign, form=ExperimentDesignForm, extra=4, max_num=4, can_delete=True)
    ExperimentLatLongFormSet = modelformset_factory(ExperimentLatLong, form=ExperimentLatLongForm, extra=2, can_delete=True)
    ExperimentPopulationFormSet = modelformset_factory(ExperimentPopulation, form=ExperimentPopulationForm, extra=2, can_delete=True)
    # This publication
    publication = Publication.objects.get(pk=publication_pk)
    # This experiment
    experiments = Experiment.objects.filter(publication=publication).order_by('pk')
    experiment = experiments[experiment_index]
    # Form for this experiment
    experiment_form = ExperimentForm(data=data, instance=experiment, prefix="experiment_form")
    experiment_form.fields['intervention'] = TreeNodeChoiceField(queryset=Intervention.objects.all().get_descendants(include_self=True), level_indicator = "---")
    # Formsets for this experiment
    experiment_population_formset = ExperimentPopulationFormSet(data=data, queryset=ExperimentPopulation.objects.filter(experiment=experiment), prefix="experiment_population_formset")
    experiment_country_formset = ExperimentCountryFormSet(data=data, queryset=ExperimentCountry.objects.filter(experiment=experiment), prefix="experiment_country_formset")
    experiment_crop_formset = ExperimentCropFormSet(data=data, queryset=ExperimentCrop.objects.filter(experiment=experiment), prefix="experiment_crop_formset")
    # Crop choices for the formset
    for form in experiment_crop_formset:
        form.fields['crop'] = TreeNodeChoiceField(queryset=Crop.objects.all().get_descendants(include_self=True), level_indicator = "---")
    experiment_date_formset = ExperimentDateFormSet(data=data, queryset=ExperimentDate.objects.filter(experiment=experiment), prefix="experiment_date_formset")
    experiment_design_formset = ExperimentDesignFormSet(data=data, queryset=ExperimentDesign.objects.filter(experiment=experiment), prefix="experiment_design_formset")
    experiment_lat_long_formset = ExperimentLatLongFormSet(data=data, queryset=ExperimentLatLong.objects.filter(experiment=experiment), prefix="experiment_lat_long_formset")
    if request.method == 'POST':
        with transaction.atomic():
            form = experiment_form
            if form.is_valid():
                form.save()
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
            formset = experiment_country_formset
            if formset.is_valid():
                instances = formset.save(commit=False)
                if 'delete' in request.POST:
                    for obj in formset.deleted_objects:
                        obj.delete()
                else:
                    for instance in instances:
                        instance.experiment = experiment
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
            formset = experiment_date_formset
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
        'experiment_form': experiment_form,
        'experiment_country_formset': experiment_country_formset,
        'experiment_crop_formset': experiment_crop_formset,
        'experiment_date_formset': experiment_date_formset,
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
    user = request.user
    subject = Subject.objects.get(slug=subject)
    context = {
        'subject': subject,  # Browse within this subject
        'interventions': Intervention.objects.all(),
    }
    if user.is_authenticated:
        status = get_status(user, subject)
        context.update(status)
    return render(request, 'publications/browse_publications_by_intervention.html', context)


def browse_publications_by_outcome(request, subject):
    user = request.user
    subject = Subject.objects.get(slug=subject)
    context = {
        'subject': subject,  # Browse within this subject
        'outcomes': Outcome.objects.all(),
    }
    if user.is_authenticated:
        status = get_status(user, subject)
        context.update(status)
    return render(request, 'publications/browse_publications_by_outcome.html', context)


def publications_by_intervention(request, subject, path, instance):
    user = request.user
    subject = Subject.objects.get(slug=subject)
    interventions = instance.get_descendants(include_self=True)
    experiments = Experiment.objects.filter(intervention__in=interventions)
    publications = Publication.objects.distinct().filter(subject=subject, experiment__in=experiments).order_by('title')
    context = {
        'subject': subject,
        'publications': publications
    }
    if user.is_authenticated:
        status = get_status(user, subject)
        context.update(status)
    return render(request, 'publications/publications.html', context)


def publications_by_outcome(request, subject, path, instance):
    user = request.user
    subject = Subject.objects.get(slug=subject)
    outcomes = instance.get_descendants(include_self=True)
    experiment_population_outcomes = ExperimentPopulationOutcome.objects.filter(outcome__in=outcomes)
    experiment_populations = ExperimentPopulation.objects.filter(experimentpopulationoutcome__in=experiment_population_outcomes)
    experiments = Experiment.objects.filter(experimentpopulation__in=experiment_populations)
    publications = Publication.objects.distinct().filter(subject=subject, experiment__in=experiments).order_by('title')
    context = {
        'subject': subject,
        'publications': publications
    }
    if user.is_authenticated:
        status = get_status(user, subject)
        context.update(status)
    return render(request, 'publications/publications.html', context)


def get_status(user, subject):
    # Publications should be assessed in a random order, but each user should see the same order from session to session. Therefore, a random assessment_order is created for each user (for each subject), and it is saved in the database.

    # If an assessment_order has been created for this user and subject, get it from the database.
    if AssessmentStatus.objects.filter(user=user, subject=subject).exists():
        item = AssessmentStatus.objects.get(user=user, subject=subject)
        assessment_order = literal_eval(item.assessment_order)
        next_assessment = item.next_assessment
        completed_assessments = literal_eval(item.completed_assessments)
        completed_full_text_assessments = literal_eval(item.completed_full_text_assessments)
        relevant_publications = literal_eval(item.relevant_publications)

        # If new publications have been added to the database, then randomly append their pks to the end of assessment_order.
        max_assessment_pks = max(assessment_order)
        pks = Publication.objects.filter(subject=subject).values_list('pk', flat=True)
        max_pks = max(pks)

        if max_assessment_pks < max_pks:
            new_publications = list(pks)
            new_publications = list(set(new_publications) - set(assessment_order))
            shuffle(new_publications)
            assessment_order = assessment_order + new_publications
            item.assessment_order = assessment_order
            item.save()

        #TODO: If old publications have been deleted from the database (this should not happen in production), then delete their pks from assessment_order.

    #TODO: This crashes if there is a subject for which no publications have yet been added to the database.
    # If an assessment_order has not been created for this user and subject, create it and save it in the database.
    else:
        pks = Publication.objects.filter(subject=subject).values_list('pk', flat=True)
        assessment_order = list(pks)
        shuffle(assessment_order)
        next_assessment = assessment_order[0]
        completed_assessments = []
        completed_full_text_assessments = []
        relevant_publications = []
        item = AssessmentStatus(
            subject=subject,
            user=user,
            assessment_order=assessment_order,
            next_assessment=next_assessment,
            completed_assessments=completed_assessments,
            completed_full_text_assessments=completed_full_text_assessments,
            relevant_publications=relevant_publications
        )
        item.save()
    item = AssessmentStatus.objects.get(user=user, subject=subject)
    publications_count = len(assessment_order)
    publications_assessed_count = len(completed_assessments)
    full_texts_assessed_count = len(completed_full_text_assessments)
    relevant_publications_count = len(relevant_publications)
    if publications_count != 0:
        publications_assessed_percent = int(publications_assessed_count / publications_count * 100)
    else:
        publications_assessed_percent = 100
    if full_texts_assessed_count != 0:
        full_texts_assessed_percent = int(full_texts_assessed_count / relevant_publications_count * 100)
    else:
        full_texts_assessed_percent = 100
    status = {
        'item': item,
        'publications_count': publications_count,
        'publications_assessed_count': publications_assessed_count,
        'publications_assessed_percent': publications_assessed_percent,
        'full_texts_assessed_count': full_texts_assessed_count,
        'full_texts_assessed_percent': full_texts_assessed_percent,
        'relevant_publications_count': relevant_publications_count,
        'next_assessment': next_assessment
    }
    return(status)


def get_next_assessment(publication_pk, next_pk, assessment_order, completed_assessments):
    next_assessment = next_pk
    for i in assessment_order:
        if next_assessment not in completed_assessments:
            if next_assessment != publication_pk:
                break
        else:
            try:
                next_assessment = assessment_order[assessment_order.index(next_assessment) + 1]
            except:
                next_assessment = assessment_order[0]
    return(next_assessment)
