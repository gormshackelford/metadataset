from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from ast import literal_eval
from random import shuffle
from .tokens import account_activation_token
from .forms import AssessmentForm, EffectForm, ExperimentForm, ExperimentCountryForm, ExperimentDateForm, ExperimentDesignForm, ExperimentLatLongForm, ExperimentLatLongDMSForm, ExperimentPopulationForm, ExperimentPopulationOutcomeForm, FullTextAssessmentForm, InterventionForm, OutcomeForm, ProfileForm, PublicationForm, PublicationCountryForm, PublicationDateForm, PublicationLatLongForm, PublicationLatLongDMSForm, PublicationPopulationForm, PublicationPopulationOutcomeForm, SignUpForm, UserForm
from .models import Assessment, AssessmentStatus, Country, Crop, Design, Experiment, ExperimentCountry, ExperimentCrop, ExperimentDate, ExperimentDesign, ExperimentLatLong, ExperimentLatLongDMS, ExperimentPopulation, ExperimentPopulationOutcome, Intervention, Outcome, Publication, PublicationCountry, PublicationDate, PublicationLatLong, PublicationLatLongDMS, PublicationPopulation, PublicationPopulationOutcome, Subject, User
from .serializers import CountrySerializer, DesignSerializer, ExperimentSerializer, ExperimentCountrySerializer, ExperimentDesignSerializer, ExperimentPopulationSerializer, ExperimentPopulationOutcomeSerializer, InterventionSerializer, OutcomeSerializer, PublicationSerializer, PublicationPopulationSerializer, PublicationPopulationOutcomeSerializer, SubjectSerializer, UserSerializer
from .decorators import group_required
from mptt.forms import TreeNodeChoiceField
from haystack.generic_views import SearchView
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet
from rest_framework import viewsets
from django_filters import rest_framework as filters
import reversion
import csv


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for "countries"
    """
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class DesignViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for "designs"
    """
    queryset = Design.objects.all()
    serializer_class = DesignSerializer


class ExperimentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for "experiments" (i.e. one "intervention" in one "publication")
    """
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer


class ExperimentCountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for "experiment countries" (i.e. one "country" in one "experiment")
    """
    queryset = ExperimentCountry.objects.distinct()
    serializer_class = ExperimentCountrySerializer


class ExperimentDesignViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for "experiment designs" (i.e. one "design" element in one "experiment")
    """
    queryset = ExperimentDesign.objects.distinct()
    serializer_class = ExperimentDesignSerializer


class ExperimentPopulationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for "experiment populations" (i.e. one "population" in one "experiment")
    """
    queryset = ExperimentPopulation.objects.all()
    serializer_class = ExperimentPopulationSerializer


class ExperimentPopulationOutcomeViewSetFilter(filters.FilterSet):
    class Meta:
        model = ExperimentPopulationOutcome
        fields = ['outcome', 'experiment_population__experiment__intervention']


class ExperimentPopulationOutcomeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for "effects" = "experiment populations outcomes" (i.e. one "outcome" for one "population" in one "experiment")
    """
    queryset = ExperimentPopulationOutcome.objects.all()
    serializer_class = ExperimentPopulationOutcomeSerializer
    filterset_class = ExperimentPopulationOutcomeViewSetFilter

    def get_queryset(self):
        queryset = ExperimentPopulationOutcome.objects.all()
        intervention_pk = self.kwargs.get('intervention_pk', None)
        if intervention_pk is not None:
            interventions = Intervention.objects.all().filter(pk=intervention_pk).get_descendants(include_self=True)
            queryset = queryset.filter(
                experiment_population__experiment__intervention__in=interventions
            )
        outcome_pk = self.kwargs.get('outcome_pk', None)
        if outcome_pk is not None:
            outcomes = Outcome.objects.all().filter(pk=outcome_pk).get_descendants(include_self=True)
            queryset = queryset.filter(
                outcome__in=outcomes
            )
        return queryset


class InterventionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for "interventions"
    """
    queryset = Intervention.objects.all()
    serializer_class = InterventionSerializer


class OutcomeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for "outcomes"
    """
    queryset = Outcome.objects.all()
    serializer_class = OutcomeSerializer


class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for "publications"
    """
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer


class PublicationPopulationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for "publication populations" (i.e. one "population" in one "publication")
    """
    queryset = PublicationPopulation.objects.all()
    serializer_class = PublicationPopulationSerializer


class PublicationPopulationOutcomeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for "publication populations outcomes" (i.e. one "outcome" for one "population" in one "publication")
    """
    queryset = PublicationPopulationOutcome.objects.all()
    serializer_class = PublicationPopulationOutcomeSerializer


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for "subjects"
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for "users"
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


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
        if Publication.objects.filter(subject=subject).exists():
            status = get_status(user, subject)
            context.update(status)
    return render(request, 'publications/subject.html', context)


def publications(request, subject, state='all', download='none'):
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
        publications = Publication.objects.distinct().filter(subject=subject).exclude(
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
    # Cannot find
    elif (state == 'cannot_find'):
        publications = Publication.objects.distinct().filter(
            assessment__in=Assessment.objects.filter(
                subject=subject,
                user=user,
                cannot_find = True
            )
        ).order_by('title')
    # Cannot find
    elif (state == 'cannot_access'):
        publications = Publication.objects.distinct().filter(
            assessment__in=Assessment.objects.filter(
                subject=subject,
                user=user,
                cannot_access = True
            )
        ).order_by('title')
    elif (state == 'secondary_literature'):
        publications = Publication.objects.distinct().filter(
            assessment__in=Assessment.objects.filter(
                subject=subject,
                user=user,
                secondary_literature = True
            )
        ).order_by('title')
    elif (state == 'other'):
        publications = Publication.objects.distinct().filter(
            assessment__in=Assessment.objects.filter(
                subject=subject,
                user=user,
                other = True
            )
        ).order_by('title')
    elif (state == 'no_pico'):
        publications = Publication.objects.distinct().filter(
            assessment__in=Assessment.objects.filter(
                subject=subject,
                user=user
            ).filter(
                Q(no_population=True) |
                Q(no_intervention=True) |
                Q(no_comparator=True) |
                Q(no_outcome=True)
            )
        ).order_by('title')
    # Publications that this user has marked as completed
    elif (state == 'completed'):
        publications = Publication.objects.distinct().filter(
            assessment__in=Assessment.objects.filter(
                subject=subject,
                user=user,
                is_completed=True
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
    # If the request is to download the publications, rather than viewing them online
    if download == 'CSV':
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="bibliography.csv"'
        # Write the CSV
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)
        writer.writerow(['Authors', 'Year', 'Title', 'Journal', 'Volume', 'Issue', 'DOI', 'URL', 'Abstract'])
        slug = subject.slug
        current_site = get_current_site(request)
        domain = current_site.domain
        for publication in publications:
            try:
                separator = ', '
                authors = separator.join(publication.author_list)
            except:
                authors = publication.authors
            path = reverse('publication', args=(), kwargs={'subject': slug, 'publication_pk': publication.pk})
            url = "http://{domain}{path}".format(domain=domain, path=path)
            writer.writerow([authors, publication.year, publication.title, publication.journal, publication.volume, publication.issue, publication.doi, url, publication.abstract])
        return response
    # If the request is not to download the publications
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
            subject = 'Metadataset'
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
    intervention = subject.intervention  # The root intervention for this subject (each subject can have its own classification of interventions)
    publication_pk = int(publication_pk)

    # Get data for the sidebar.
    status = get_status(user, subject)
    item = status.get('item')  # item = AssessmentStatus instance for this user and subject
    assessment_order = literal_eval(item.assessment_order)
    completed_assessments = literal_eval(item.completed_assessments)

    # The next pk and previous pk in assessment_order, to be used for navigation
    try:
        previous_pk = assessment_order[assessment_order.index(publication_pk) - 1]
    except:
        previous_pk = assessment_order[0]
    try:
        next_pk = assessment_order[assessment_order.index(publication_pk) + 1]
    except:
        next_pk = assessment_order[0]

    ExperimentFormSet = modelformset_factory(Experiment, form=ExperimentForm, extra=4, can_delete=True)
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
                    assessment.is_completed = False
                    assessment.full_text_is_relevant = None
                    assessment.cannot_find = False
                    assessment.cannot_access = False
                    assessment.secondary_literature = False
                    assessment.no_population = False
                    assessment.no_intervention = False
                    assessment.no_outcome = False
                    assessment.no_comparator = False
                    assessment.other = False
                    assessment.note = ''
                    assessment.save()
                    # Update status and get next assessment
                    if publication_pk not in completed_assessments:
                        completed_assessments.append(publication_pk)
                        item.completed_assessments = completed_assessments
                    next_assessment = get_next_assessment(publication_pk, next_pk, assessment_order, completed_assessments)
                    item.next_assessment = next_assessment
                    item.save()
                    return redirect('publication', subject=subject.slug, publication_pk=next_assessment)
        if 'is_not_relevant' in request.POST:
            with transaction.atomic():
                if assessment_form.is_valid():
                    # Update assessment
                    assessment = assessment_form.save(commit=False)
                    assessment.user = user
                    assessment.publication = publication
                    assessment.subject = subject
                    assessment.is_relevant = False
                    assessment.is_completed = False
                    assessment.full_text_is_relevant = None
                    assessment.cannot_find = False
                    assessment.cannot_access = False
                    assessment.secondary_literature = False
                    assessment.no_population = False
                    assessment.no_intervention = False
                    assessment.no_outcome = False
                    assessment.no_comparator = False
                    assessment.other = False
                    assessment.note = ''
                    assessment.save()
                    # Update status and get next assessment
                    if publication_pk not in completed_assessments:
                        completed_assessments.append(publication_pk)
                        item.completed_assessments = completed_assessments
                    next_assessment = get_next_assessment(publication_pk, next_pk, assessment_order, completed_assessments)
                    item.next_assessment = next_assessment
                    item.save()
                    return redirect('publication', subject=subject.slug, publication_pk=next_assessment)
        if 'full_text_is_not_relevant' in request.POST:
            with transaction.atomic():
                if full_text_assessment_form.is_valid():
                    # Update assessments (add the reason for rejection)
                    assessment = full_text_assessment_form.save(commit=False)
                    assessment.user = user
                    assessment.publication = publication
                    assessment.subject = subject
                    assessment.is_relevant = True  # It must be relevant based on the title and abstract if it is to be rejected based on the full text.
                    assessment.is_completed = True
                    assessment.full_text_is_relevant = False
                    assessment.save()
                    # Update status and get next assessment
                    if publication_pk not in completed_assessments:
                        completed_assessments.append(publication_pk)
                        item.completed_assessments = completed_assessments
                    next_assessment = get_next_assessment(publication_pk, next_pk, assessment_order, completed_assessments)
                    item.next_assessment = next_assessment
                    item.save()
                return redirect('publication', subject=subject.slug, publication_pk=publication_pk)
        if 'save' in request.POST or 'delete' in request.POST:
            with transaction.atomic():
                # Before the formset is validated, the choices need to be redefined, or the validation will fail. This is because only a subset of all choices (high level choices in the MPTT tree) were initially shown in the dropdown (for better UI).
                interventions = TreeNodeChoiceField(queryset=Intervention.objects.filter(pk=intervention.pk).get_descendants(include_self=True), level_indicator = "---")
                for form in formset:
                    form.fields['intervention'] = interventions
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
                    if full_text_assessment_form.is_valid():
                        # If an intervention has been selected, mark this publication as "relevant" to this systematic map.
                        # Check if this publication was already marked as "completed" before saving the form. If it was, mark it as not "completed" (because a new intervention has been added, and the user will need to add new metadata).
                        if Experiment.objects.filter(publication=publication, user=user).exists():
                            if Assessment.objects.filter(publication=publication, user=user).exists():
                                old_assessment = Assessment.objects.get(publication=publication, user=user)
                                was_completed = old_assessment.is_completed
                            else:
                                was_completed = False
                            # Get the form data for the new assessment.
                            assessment = full_text_assessment_form.save(commit=False)
                            if was_completed == True:
                                assessment.is_completed = False
                            else:
                                assessment.is_completed = assessment.is_completed
                            assessment.user = user
                            assessment.publication = publication
                            assessment.subject = subject
                            assessment.is_relevant = True
                            assessment.full_text_is_relevant = True
                            assessment.cannot_find = False
                            assessment.cannot_access = False
                            assessment.secondary_literature = False
                            assessment.no_population = False
                            assessment.no_intervention = False
                            assessment.no_outcome = False
                            assessment.no_comparator = False
                            assessment.other = False
                            assessment.note = ''
                            assessment.save()
                            # Update status and get next assessment
                            if publication_pk not in completed_assessments:
                                completed_assessments.append(publication_pk)
                                item.completed_assessments = completed_assessments
                            next_assessment = get_next_assessment(publication_pk, next_pk, assessment_order, completed_assessments)
                            item.next_assessment = next_assessment
                            item.save()
                        # If all interventions have been deleted, remove this publication from the completed assessments.
                        elif 'delete' in request.POST:
                            if publication_pk in completed_assessments:
                                completed_assessments.remove(publication_pk)
                                item.completed_assessments = completed_assessments
                            next_assessment = publication_pk
                            item.next_assessment = next_assessment
                            item.save()
                            if Assessment.objects.filter(publication=publication, user=user).exists():
                                Assessment.objects.filter(publication=publication, user=user).delete()
                return redirect('publication', subject=subject.slug, publication_pk=publication_pk)
    else:
        # Intervention choices for the formset (high-level choices only)
        interventions = TreeNodeChoiceField(required=False, queryset=Intervention.objects.filter(pk=intervention.pk).get_descendants(include_self=True).filter(level__lte=2).filter(level__gt=0), level_indicator = "---")
        for form in formset:
            form.fields['intervention'] = interventions
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
def metadata(request, subject, publication_pk):
    """
    On this page, the user edits the publication-level metadata for this publication (i.e. metadata that is applicable to all interventions).
    """
    user = request.user
    data = request.POST or None
    subject = Subject.objects.get(slug=subject)
    outcome = subject.outcome  # The root outcome for this subject (each subject can have its own classification of outcomes)
    publication_pk = int(publication_pk)
    PublicationCountryFormSet = modelformset_factory(PublicationCountry, form=PublicationCountryForm, extra=2, can_delete=True)
    PublicationDateFormSet = modelformset_factory(PublicationDate, form=PublicationDateForm, extra=2, max_num=2, can_delete=True)
    PublicationLatLongFormSet = modelformset_factory(PublicationLatLong, form=PublicationLatLongForm, extra=1, can_delete=True)
    PublicationLatLongDMSFormSet = modelformset_factory(PublicationLatLongDMS, form=PublicationLatLongDMSForm, extra=1, can_delete=True)
    PublicationPopulationFormSet = modelformset_factory(PublicationPopulation, form=PublicationPopulationForm, extra=4, can_delete=True)
    # This publication
    publication = Publication.objects.get(pk=publication_pk)
    # Formsets for this publication
    publication_country_formset = PublicationCountryFormSet(data=data, queryset=PublicationCountry.objects.filter(publication=publication), prefix="publication_country_formset")
    publication_date_formset = PublicationDateFormSet(data=data, queryset=PublicationDate.objects.filter(publication=publication), prefix="publication_date_formset")
    publication_lat_long_formset = PublicationLatLongFormSet(data=data, queryset=PublicationLatLong.objects.filter(publication=publication), prefix="publication_lat_long_formset")
    publication_lat_long_dms_formset = PublicationLatLongDMSFormSet(data=data, queryset=PublicationLatLongDMS.objects.filter(publication=publication), prefix="publication_lat_long_dms_formset")
    publication_population_formset = PublicationPopulationFormSet(data=data, queryset=PublicationPopulation.objects.filter(publication=publication), prefix="publication_population_formset")
    if request.method == 'POST':
        if 'save' in request.POST or 'delete' in request.POST:
            with transaction.atomic():
                formset = publication_country_formset
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
                formset = publication_date_formset
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
                formset = publication_lat_long_formset
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
                formset = publication_lat_long_dms_formset
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
                formset = publication_population_formset
                # Before the formset is validated, the choices need to be redefined, or the validation will fail. This is because only a subset of all choices (high level choices in the MPTT tree) were initially shown in the dropdown (for better UI).
                populations = TreeNodeChoiceField(queryset=Outcome.objects.filter(pk=outcome.pk).get_descendants(include_self=True), level_indicator = "---")
                for form in formset:
                    form.fields['population'] = populations
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
                return redirect('metadata', subject=subject.slug, publication_pk=publication_pk)
    else:
        # Population choices for the formset (populations are the level 1 in the classification of outcomes; level 0 is for different subjects, and here we only show the populations/outcomes for this subject, at level=1)
        populations = TreeNodeChoiceField(required=False, queryset=Outcome.objects.filter(pk=outcome.pk).get_descendants(include_self=True).filter(level=1), level_indicator = "---")
        for form in publication_population_formset:
            form.fields['population'] = populations
    context = {
        'subject': subject,
        'publication': publication,
        'publication_country_formset': publication_country_formset,
        'publication_date_formset': publication_date_formset,
        'publication_lat_long_formset': publication_lat_long_formset,
        'publication_lat_long_dms_formset': publication_lat_long_dms_formset,
        'publication_population_formset': publication_population_formset
    }
    return render(request, 'publications/metadata.html', context)


@login_required
def publication_population(request, subject, publication_pk, publication_population_index):
    """
    On this page, the user chooses an outcome for this publication population (not for a specific intervention).
    """
    user = request.user
    data = request.POST or None
    subject = Subject.objects.get(slug=subject)
    outcome = subject.outcome  # The root outcome for this subject (each subject can have its own classification of outcomes)
    PublicationPopulationOutcomeFormSet = modelformset_factory(PublicationPopulationOutcome, form=PublicationPopulationOutcomeForm, extra=4, can_delete=True)
    # This publication
    publication = Publication.objects.get(pk=publication_pk)
    # This publication_population
    publication_populations = PublicationPopulation.objects.filter(publication=publication).order_by('pk')
    publication_population = publication_populations[publication_population_index]
    # Formset for this publication_population
    formset = PublicationPopulationOutcomeFormSet(data=data, queryset=PublicationPopulationOutcome.objects.filter(publication_population=publication_population), prefix="publication_population_outcome_formset")
    # Outcome choices for the formset
    for form in formset:
        form.fields['outcome'] = TreeNodeChoiceField(queryset=Outcome.objects.get(pk=publication_population.population.pk).get_descendants(include_self=True), level_indicator = "---")
    if request.method == 'POST':
        with transaction.atomic():
            if formset.is_valid():
                instances = formset.save(commit=False)
                if 'delete' in request.POST:
                    for obj in formset.deleted_objects:
                        obj.delete()
                else:
                    for instance in instances:
                        instance.publication_population = publication_population
                        instance.user = user
                        instance.save()
            return redirect('publication_population', subject=subject.slug, publication_pk=publication_pk, publication_population_index=publication_population_index)
    context = {
        'subject': subject,
        'publication': publication,
        'publication_population': publication_population,
        'publication_population_index': publication_population_index,
        'formset': formset
    }
    return render(request, 'publications/publication_population.html', context)


@login_required
@group_required('can_edit_publications')
def edit_publication(request, subject, publication_pk):
    """
    On this page, the user edits the title, abstract, etc. for this publication.
    """
    user = request.user
    data = request.POST or None
    subject = Subject.objects.get(slug=subject)
    publication_pk = int(publication_pk)
    publication = Publication.objects.get(pk=publication_pk)
    if request.method == 'POST':
        publication_form = PublicationForm(request.POST, instance=publication)
        if publication_form.is_valid():
            with reversion.create_revision():  # Version control (django-revision)
                publication_form.save()
                reversion.set_user(request.user)
        return redirect('publication', subject=subject.slug, publication_pk=publication_pk)
    else:
        publication_form = PublicationForm(instance=publication)
    context = {
        'subject': subject,
        'publication': publication,
        'publication_form': publication_form
    }
    # Get data for the sidebar.
    status = get_status(user, subject)
    context.update(status)
    return render(request, 'publications/edit_publication.html', context)


@login_required
def experiment(request, subject, publication_pk, experiment_index):
    """
    On this page, the user chooses populations, experimental designs, and tags for this intervention (i.e. this "experiment").
    """
    user = request.user
    data = request.POST or None
    subject = Subject.objects.get(slug=subject)
    design = subject.design  # The root design for this subject (each subject can have its own classification of designs)
    intervention = subject.intervention  # The root intervention for this subject (each subject can have its own classification of interventions)
    outcome = subject.outcome  # The root outcome for this subject (each subject can have its own classification of outcomes)
    ExperimentFormSet = modelformset_factory(Experiment, form=ExperimentForm, extra=0, can_delete=False)
    ExperimentCountryFormSet = modelformset_factory(ExperimentCountry, form=ExperimentCountryForm, extra=2, can_delete=True)
    ExperimentDateFormSet = modelformset_factory(ExperimentDate, form=ExperimentDateForm, extra=2, max_num=2, can_delete=True)
    ExperimentDesignFormSet = modelformset_factory(ExperimentDesign, form=ExperimentDesignForm, extra=5, max_num=5, can_delete=True)
    ExperimentLatLongFormSet = modelformset_factory(ExperimentLatLong, form=ExperimentLatLongForm, extra=1, can_delete=True)
    ExperimentLatLongDMSFormSet = modelformset_factory(ExperimentLatLongDMS, form=ExperimentLatLongDMSForm, extra=1, can_delete=True)
    ExperimentPopulationFormSet = modelformset_factory(ExperimentPopulation, form=ExperimentPopulationForm, extra=4, can_delete=True)
    # This publication
    publication = Publication.objects.get(pk=publication_pk)
    # This experiment
    experiments = Experiment.objects.filter(publication=publication).order_by('pk')
    experiment = experiments[experiment_index]
    # Form for this experiment
    experiment_form = ExperimentForm(data=data, instance=experiment, prefix="experiment_form")
    # Show interventions for only this subject (level 0 in the classification of interventions is for different subjects, and here we show interventions for only this subject)
    experiment_form.fields['intervention'] = TreeNodeChoiceField(queryset=Intervention.objects.filter(pk=intervention.pk).get_descendants(include_self=True), level_indicator = "---")
    # Formsets for this experiment
    experiment_population_formset = ExperimentPopulationFormSet(data=data, queryset=ExperimentPopulation.objects.filter(experiment=experiment), prefix="experiment_population_formset")
    experiment_country_formset = ExperimentCountryFormSet(data=data, queryset=ExperimentCountry.objects.filter(experiment=experiment), prefix="experiment_country_formset")
    experiment_date_formset = ExperimentDateFormSet(data=data, queryset=ExperimentDate.objects.filter(experiment=experiment), prefix="experiment_date_formset")
    experiment_design_formset = ExperimentDesignFormSet(data=data, queryset=ExperimentDesign.objects.filter(experiment=experiment), prefix="experiment_design_formset")
    experiment_lat_long_formset = ExperimentLatLongFormSet(data=data, queryset=ExperimentLatLong.objects.filter(experiment=experiment), prefix="experiment_lat_long_formset")
    experiment_lat_long_dms_formset = ExperimentLatLongDMSFormSet(data=data, queryset=ExperimentLatLongDMS.objects.filter(experiment=experiment), prefix="experiment_lat_long_dms_formset")
    if request.method == 'POST':
        with transaction.atomic():
            form = experiment_form
            if form.is_valid():
                form.save()
            formset = experiment_population_formset
            # Before the formset is validated, the choices need to be redefined, or the validation will fail. This is because only a subset of all choices (high level choices in the MPTT tree) were initially shown in the dropdown (for better UI).
            populations = TreeNodeChoiceField(queryset=Outcome.objects.filter(pk=outcome.pk).get_descendants(include_self=True), level_indicator = "---")
            for form in formset:
                form.fields['population'] = populations
            if formset.is_valid():
                instances = formset.save(commit=False)
                if 'delete' in request.POST:
                    for obj in formset.deleted_objects:
                        obj.delete()
                else:
                    for instance in instances:
                        instance.experiment = experiment
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
            # Before the formset is validated, the choices need to be redefined, or the validation will fail. This is because only a subset of all choices (high level choices in the MPTT tree) were initially shown in the dropdown (for better UI).
            designs = TreeNodeChoiceField(queryset=Design.objects.filter(pk=design.pk).get_descendants(include_self=True), level_indicator = "---")
            for form in formset:
                form.fields['design'] = designs
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
            formset = experiment_lat_long_dms_formset
            if formset.is_valid():
                instances = formset.save(commit=False)
                if 'delete' in request.POST:
                    for obj in formset.deleted_objects:
                        obj.delete()
                else:
                    for instance in instances:
                        instance.experiment = experiment
                        instance.save()
            return redirect('experiment', subject=subject.slug, publication_pk=publication_pk, experiment_index=experiment_index)
    else:
        # Population choices for the formset (populations are the level 1 in the classification of outcomes; level 0 is for different subjects, and here we only show the populations/outcomes for this subject, at level=1)
        populations = TreeNodeChoiceField(required=False, queryset=Outcome.objects.filter(pk=outcome.pk).get_descendants(include_self=True).filter(level=1), level_indicator = "---")
        for form in experiment_population_formset:
            form.fields['population'] = populations
        # Design choices for the formset (level 0 in the classification of designs is for different subjects, and here we only show the classification for this subject, at level__gte=1)
        designs = TreeNodeChoiceField(required=False, queryset=Design.objects.filter(pk=design.pk).get_descendants(include_self=True).filter(level__gte=1), level_indicator = "---")
        for form in experiment_design_formset:
            form.fields['design'] = designs
    context = {
        'subject': subject,
        'publication': publication,
        'experiment': experiment,
        'experiment_index': experiment_index,
        'experiment_form': experiment_form,
        'experiment_country_formset': experiment_country_formset,
        'experiment_date_formset': experiment_date_formset,
        'experiment_design_formset': experiment_design_formset,
        'experiment_lat_long_formset': experiment_lat_long_formset,
        'experiment_lat_long_dms_formset': experiment_lat_long_dms_formset,
        'experiment_population_formset': experiment_population_formset
    }
    return render(request, 'publications/experiment.html', context)


@login_required
def population(request, subject, publication_pk, experiment_index, population_index):
    """
    On this page, the user chooses outcomes for this population.
    """
    data = request.POST or None
    subject = Subject.objects.get(slug=subject)
    ExperimentPopulationOutcomeFormSet = modelformset_factory(ExperimentPopulationOutcome, form=ExperimentPopulationOutcomeForm, extra=4, can_delete=True)
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
        form.fields['outcome'] = TreeNodeChoiceField(queryset=Outcome.objects.get(pk=experiment_population.population.pk).get_descendants(include_self=True), level_indicator = "---")
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
            return redirect('population', subject=subject.slug, publication_pk=publication_pk, experiment_index=experiment_index, population_index=population_index)
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
    On this page, the user enters effect sizes and related data for this outcome.
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
            return redirect('outcome', subject=subject.slug, publication_pk=publication_pk, experiment_index=experiment_index, population_index=population_index, outcome_index=outcome_index)
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


def browse_by_intervention(request, subject, state='default'):  #TODO: delete default and test
    user = request.user
    subject = Subject.objects.get(slug=subject)
    intervention = subject.intervention    # The root intervention for this subject (each subject can have its own classification of interventions)
    interventions = Intervention.objects.filter(pk=intervention.pk).get_descendants(include_self=True)
    context = {
        'subject': subject,  # Browse within this subject
        'state': state,  # Browse either publications or effects
        'interventions': interventions,
    }
    if user.is_authenticated:
        if Publication.objects.filter(subject=subject).exists():
            status = get_status(user, subject)
            context.update(status)
    return render(request, 'publications/browse_by_intervention.html', context)


def browse_by_outcome(request, subject, state='default'):  #TODO: delete default and test
    user = request.user
    subject = Subject.objects.get(slug=subject)
    outcome = subject.outcome
    outcomes = Outcome.objects.filter(pk=outcome.pk).get_descendants(include_self=True)
    context = {
        'subject': subject,  # Browse within this subject
        'state': state,  # Browse either publications or effects
        'outcomes': outcomes
    }
    if user.is_authenticated:
        if Publication.objects.filter(subject=subject).exists():
            status = get_status(user, subject)
            context.update(status)
    return render(request, 'publications/browse_by_outcome.html', context)


def publications_by_intervention(request, subject, path, instance):
    user = request.user
    subject = Subject.objects.get(slug=subject)
    interventions = instance.get_descendants(include_self=True)
    experiments = Experiment.objects.filter(intervention__in=interventions)
    publications = Publication.objects.distinct().filter(subject=subject, experiment__in=experiments).order_by('title')
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
        if Publication.objects.filter(subject=subject).exists():
            status = get_status(user, subject)
            context.update(status)
    return render(request, 'publications/publications.html', context)


def publications_by_outcome(request, subject, path, instance):
    user = request.user
    subject = Subject.objects.get(slug=subject)
    outcomes = instance.get_descendants(include_self=True)
    # Outcomes related to interventions within publications
    experiment_population_outcomes = ExperimentPopulationOutcome.objects.filter(outcome__in=outcomes)
    experiment_populations = ExperimentPopulation.objects.filter(experimentpopulationoutcome__in=experiment_population_outcomes)
    experiments = Experiment.objects.filter(experimentpopulation__in=experiment_populations)
    # Outcomes related to publications
    publication_population_outcomes = PublicationPopulationOutcome.objects.filter(outcome__in=outcomes)
    publication_populations = PublicationPopulation.objects.filter(publicationpopulationoutcome__in=publication_population_outcomes)
    # Publications based on both of the above sources of outcomes
    publications = Publication.objects.distinct().filter(subject=subject).filter(
            Q(experiment__in=experiments) |
            Q(publicationpopulation__in=publication_populations)
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
        if Publication.objects.filter(subject=subject).exists():
            status = get_status(user, subject)
            context.update(status)
    return render(request, 'publications/publications.html', context)


def effects_by_intervention(request, subject, path, instance):
    user = request.user
    subject = Subject.objects.get(slug=subject)
    interventions = instance.get_descendants(include_self=True)
    experiments = Experiment.objects.distinct().filter(intervention__in=interventions)
    populations = ExperimentPopulation.objects.distinct().filter(experiment__in=experiments)
    outcomes = ExperimentPopulationOutcome.objects.distinct().filter(experiment_population__in=populations)
    page = request.GET.get('page', 1)
    paginator = Paginator(outcomes, 10)
    try:
        outcomes = paginator.page(page)
    except PageNotAnInteger:
        outcomes = paginator.page(1)
    except EmptyPage:
        outcomes = paginator.page(paginator.num_pages)
    context = {
        'subject': subject,
        'outcomes': outcomes
    }
    if user.is_authenticated:
        if Publication.objects.filter(subject=subject).exists():
            status = get_status(user, subject)
            context.update(status)
    return render(request, 'publications/effects.html', context)


def effects_by_outcome(request, subject, path, instance):
    user = request.user
    subject = Subject.objects.get(slug=subject)
    outcomes = instance.get_descendants(include_self=True)
    outcomes = ExperimentPopulationOutcome.objects.distinct().filter(outcome__in=outcomes)
    page = request.GET.get('page', 1)
    paginator = Paginator(outcomes, 10)
    try:
        outcomes = paginator.page(page)
    except PageNotAnInteger:
        outcomes = paginator.page(1)
    except EmptyPage:
        outcomes = paginator.page(paginator.num_pages)
    context = {
        'subject': subject,
        'outcomes': outcomes
    }
    if user.is_authenticated:
        if Publication.objects.filter(subject=subject).exists():
            status = get_status(user, subject)
            context.update(status)
    return render(request, 'publications/effects.html', context)


def get_status(user, subject):
    # Publications should be assessed in a random order, but each user should see the same order from session to session. Therefore, a random assessment_order is created for each user (for each subject), and it is saved in the database.

    # If an assessment_order has been created for this user and subject, get it from the database.
    if AssessmentStatus.objects.filter(user=user, subject=subject).exists():
        item = AssessmentStatus.objects.get(user=user, subject=subject)
        assessment_order = literal_eval(item.assessment_order)
        next_assessment = item.next_assessment
        completed_assessments = literal_eval(item.completed_assessments)

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

    # If an assessment_order has not been created for this user and subject, create it and save it in the database.
    else:
        pks = Publication.objects.filter(subject=subject).values_list('pk', flat=True)
        assessment_order = list(pks)
        shuffle(assessment_order)
        next_assessment = assessment_order[0]
        previous_full_text_assessment = -1
        completed_assessments = []
        item = AssessmentStatus(
            subject=subject,
            user=user,
            assessment_order=assessment_order,
            next_assessment=next_assessment,
            previous_full_text_assessment=previous_full_text_assessment,
            completed_assessments=completed_assessments
        )
        item.save()
    item = AssessmentStatus.objects.get(user=user, subject=subject)
    publications_count = len(assessment_order)
    publications_assessed_count = len(completed_assessments)
    if publications_count != 0:
        publications_assessed_percent = int(publications_assessed_count / publications_count * 100)
    else:
        publications_assessed_percent = 100
    # Count the publications that have been assessed as relevant based on the title/abstract
    if Publication.objects.filter(assessment__in=Assessment.objects.filter(
        subject=subject, user=user, is_relevant=True)).exists():
        relevant_publications_count = Publication.objects.filter(
            assessment__in=Assessment.objects.filter(
                subject=subject, user=user, is_relevant=True)).count()
    else:
        relevant_publications_count = 0
    # Count the publications that have been marked as completed
    if Publication.objects.filter(assessment__in=Assessment.objects.filter(
        subject=subject, user=user, is_completed=True)).exists():
        full_texts_assessed_count = Publication.objects.filter(
            assessment__in=Assessment.objects.filter(
                subject=subject, user=user, is_completed=True)).count()
    else:
        full_texts_assessed_count = 0
    if relevant_publications_count != 0:
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


# This method is needed (as are the lists of completed_assessments), because
# we need to maintain a unique random order for each user. Otherwise, we could
# use querysets for navigation, as we do for full_text_navigation.
def get_next_assessment(publication_pk, next_pk, assessment_order, completed_assessments):
    next_assessment = next_pk
    if (len(completed_assessments) != len(assessment_order)):  # If all assessments have not yet been completed
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


@login_required
def full_text_navigation(request, subject, state, publication_pk='default'):
    user = request.user
    subject = Subject.objects.get(slug=subject)
    # Get the publication from which to calculate "next" and "previous" (either the previous_full_text_assessment or the publication from which the request was sent).
    if (publication_pk=='default'):
        previous_full_text_assessment = AssessmentStatus.objects.get(
            subject=subject, user=user).previous_full_text_assessment
        if (previous_full_text_assessment == -1):  # If this is a new user, the initial value will be -1.
            previous_full_text_assessment = Publication.objects.filter(
                subject=subject
            ).order_by('-title').values_list('pk', flat=True)[0]
            assessment_status = AssessmentStatus.objects.get(
                subject=subject, user=user)
            assessment_status.previous_full_text_assessment = previous_full_text_assessment
            assessment_status.save
        publication = Publication.objects.get(pk=previous_full_text_assessment)
    else:
        publication = Publication.objects.get(pk=int(publication_pk))
    # Get all the publications.
    publications = Publication.objects.filter(subject=subject)
    # Exclude this publication.
    publications = publications.exclude(pk=publication.pk)
    if (state == 'next-incomplete' or state == 'previous-incomplete'):
        # If there are publications for this subject that this user has assessed as relevant and has not yet marked as completed
        if publications.filter(assessment__in=Assessment.objects.filter(
            subject=subject, user=user, is_relevant=True, is_completed=False
        )).exists():
            publications = publications.filter(assessment__in=Assessment.objects.filter(
                subject=subject, user=user, is_relevant=True, is_completed=False
            ))
        # Else if there are publications for this subject that this user has assessed as relevant but all of them have been marked as completed
        elif publications.filter(assessment__in=Assessment.objects.filter(
            subject=subject, user=user, is_relevant=True
        )).exists():
            publications = publications.filter(assessment__in=Assessment.objects.filter(
                subject=subject, user=user, is_relevant=True
            ))
        if (state == 'next-incomplete'):
            try:
                publication_pk = publications.filter(
                    title__gte=publication.title  # Titles later in the alphabet
                ).order_by('title').values_list('pk', flat=True)[0]
            except:
                publication_pk = publications.order_by('title').values_list('pk', flat=True)[0]
        elif (state == 'previous-incomplete'):
            try:
                publication_pk = publications.filter(
                    title__lte=publication.title  # Titles earlier in the alphabet
                ).order_by('-title').values_list('pk', flat=True)[0]
            except:
                publication_pk = publications.order_by('-title').values_list('pk', flat=True)[0]
    elif (state == 'next' or state == 'previous'):
        if publications.filter(assessment__in=Assessment.objects.filter(
            subject=subject, user=user, is_relevant=True
        )).exists():
            publications = publications.filter(assessment__in=Assessment.objects.filter(
                subject=subject, user=user, is_relevant=True
            ))
            if (state == 'next'):
                try:
                    publication_pk = publications.filter(
                        title__gte=publication.title  # Titles later in the alphabet
                    ).order_by('title').values_list('pk', flat=True)[0]
                except:
                    publication_pk = publications.order_by('title').values_list('pk', flat=True)[0]
            elif (state == 'previous'):
                try:
                    publication_pk = publications.filter(
                        title__lte=publication.title  # Titles earlier in the alphabet
                    ).order_by('-title').values_list('pk', flat=True)[0]
                except:
                    publication_pk = publications.order_by('-title').values_list('pk', flat=True)[0]
    # If there are no full texts for this subject that the user has assessed as relevant
    if not publications.filter(assessment__in=Assessment.objects.filter(
        subject=subject, user=user, is_relevant=True
    )).exists():
        publication_pk = Publication.objects.filter(
            subject=subject
        ).order_by('title').values_list('pk', flat=True)[0]
    # Update the current full_text_assessment
    assessment_status = AssessmentStatus.objects.get(subject=subject, user=user)
    assessment_status.previous_full_text_assessment = publication_pk
    assessment_status.save()
    return redirect('publication', subject=subject.slug, publication_pk=publication_pk)
