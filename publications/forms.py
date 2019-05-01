from django import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from ast import literal_eval
from mptt.forms import TreeNodeChoiceField
from .models import Assessment, Attribute, Coordinates, Data, Date, EAV, Experiment, ExperimentDesign, ExperimentPopulation, ExperimentPopulationOutcome, Intervention, Outcome, Profile, Publication, PublicationPopulation, PublicationPopulationOutcome, User, XCountry


class SignUpForm(UserCreationForm):
    institution = forms.CharField(max_length=255)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address has already been registered.')
        return email


class UserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileForm(forms.ModelForm):
    institution = forms.CharField(max_length=255)

    class Meta:
        model = Profile
        fields = ['institution']


class AssessmentForm(forms.ModelForm):

    class Meta:
        model = Assessment
        fields = []


class FullTextAssessmentForm(forms.ModelForm):

    class Meta:
        model = Assessment
        fields = ['cannot_find', 'cannot_access', 'secondary_literature',
            'no_population', 'no_intervention', 'no_comparator', 'no_outcome',
            'other', 'note', 'is_completed']


class PublicationForm(forms.ModelForm):

    class Meta:
        model = Publication
        exclude = ['subject', 'is_from_systematic_search']
        widgets = {
            'authors': forms.TextInput(attrs={
                'placeholder': "Use commas and square brackets: ['Darwin, C.', 'Wallace, A. R.']"
            }),
            'pages': forms.TextInput(attrs={
                'placeholder': '1-10'
            }),
            'doi': forms.TextInput(attrs={
                'placeholder': '10.1186/s13750-018-0142-2'
            })
        }

    def clean_authors(self):
        # authors must be a Python list
        authors = self.cleaned_data['authors']
        try:
            authors = literal_eval(authors)
            if type(authors) is list:
                return authors
        except:
            authors = ''
            return authors


class DateForm(forms.ModelForm):

    class Meta:
        model = Date
        fields = ['start_year', 'end_year', 'start_month', 'end_month', 'start_day', 'end_day']


class PublicationPopulationForm(forms.ModelForm):

    class Meta:
        model = PublicationPopulation
        exclude = ['publication', 'user']


class PublicationPopulationOutcomeForm(forms.ModelForm):

    class Meta:
        model = PublicationPopulationOutcome
        exclude = ['publication_population', 'user']


class InterventionForm(forms.ModelForm):
    intervention = TreeNodeChoiceField(required=False, queryset=Intervention.objects.all().get_descendants(include_self=True), level_indicator = "---")

    class Meta:
        model = Intervention
        fields = ['intervention']


class OutcomeForm(forms.ModelForm):
    outcome = TreeNodeChoiceField(required=False, queryset=Outcome.objects.all().get_descendants(include_self=True), level_indicator = "---")

    class Meta:
        model = Outcome
        fields = ['outcome']


class ExperimentForm(forms.ModelForm):

    class Meta:
        model = Experiment
        exclude = ['publication', 'user']


class ExperimentDesignForm(forms.ModelForm):

    class Meta:
        model = ExperimentDesign
        exclude = ['experiment']


class CoordinatesForm(forms.ModelForm):
    latitude_degrees = forms.FloatField(min_value=0.0, max_value=90.0, required=False)
    latitude_minutes = forms.FloatField(min_value=0.0, max_value=60.0, required=False)
    latitude_seconds = forms.FloatField(min_value=0.0, max_value=60.0, required=False)
    longitude_degrees = forms.FloatField(min_value=0.0, max_value=180.0, required=False)
    longitude_minutes = forms.FloatField(min_value=0.0, max_value=60.0, required=False)
    longitude_seconds = forms.FloatField(min_value=0.0, max_value=60.0, required=False)

    class Meta:
        model = Coordinates
        fields = [
            'latitude_degrees', 'latitude_minutes', 'latitude_seconds',
            'latitude_direction', 'longitude_degrees', 'longitude_minutes',
            'longitude_seconds', 'longitude_direction'
        ]


class XCountryForm(forms.ModelForm):

    class Meta:
        model = XCountry
        fields = ['country']


class ExperimentPopulationForm(forms.ModelForm):

    class Meta:
        model = ExperimentPopulation
        fields = ['population']


class ExperimentPopulationOutcomeForm(forms.ModelForm):

    class Meta:
        model = ExperimentPopulationOutcome
        fields = ['outcome']


class DataForm(forms.ModelForm):
    treatment_sd = forms.FloatField(min_value=0, required=False, help_text="Standard deviation of the treatment mean")
    control_sd = forms.FloatField(min_value=0, required=False, help_text="Standard deviation of the control mean")
    treatment_n = forms.IntegerField(min_value=0, required=False, help_text="Number of replicates for the treatment")
    control_n = forms.IntegerField(min_value=0, required=False, help_text="Number of replicates for the control")
    treatment_se = forms.FloatField(min_value=0, required=False, help_text="Standard error of the treatment mean")
    control_se = forms.FloatField(min_value=0, required=False, help_text="Standard error of the control mean")
    n = forms.IntegerField(min_value=0, required=False, help_text="Number of replicates (only if treatment N and control N are unavailable)")
    lsd = forms.FloatField(min_value=0, required=False, help_text="Least significant difference between the means")
    p_value = forms.FloatField(min_value=0, max_value=1.0, required=False)
    correlation_coefficient = forms.FloatField(min_value=-1.0, max_value=1.0, required=False, help_text="Pearson correlation coefficient (r)")
    se = forms.FloatField(min_value=0, required=False, help_text="Standard error of the effect size")
    variance = forms.FloatField(min_value=0, required=False, help_text="Variance of the effect size")
    confidence = forms.FloatField(min_value=0, max_value=100, required=False, help_text="Confidence of the confidence interval (percent)")

    class Meta:
        model = Data
        exclude = ['subject', 'publication', 'experiment', 'experiment_population', 'experiment_population_outcome']
        widgets = {
            'comparison': forms.TextInput(attrs={
                'placeholder': 'e.g., "Plots with cover crops (treatment) compared to plots without cover crops (control)"'
            }),
            'unit': forms.TextInput(attrs={
                'placeholder': 'e.g., "kg/ha"'
            })
        }


class AttributeForm(forms.ModelForm):

    class Meta:
        model = Attribute
        exclude = ['slug', 'user']
        widgets = {
            'attribute': forms.TextInput(attrs={
                'placeholder': 'e.g., "Application rate" or "Herbicide type"'
            }),
            'unit': forms.TextInput(attrs={
                'placeholder': 'e.g., "kg/ha" (only if the data type is "Number")'
            })
        }

    def __init__(self, *args, **kwargs):
        super(AttributeForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['type'].disabled = True


class AttributeOptionForm(forms.ModelForm):

    class Meta:
        model = Attribute
        exclude = ['slug', 'type', 'user']
        widgets = {
            'attribute': forms.TextInput(attrs={
                'placeholder': 'e.g., "Yes" or "No"'
            })
        }


class EAVExperimentForm(forms.ModelForm):

    class Meta:
        model = EAV
        exclude = ['outcome', 'population', 'publication', 'note']


class EAVPopulationForm(forms.ModelForm):

    class Meta:
        model = EAV
        exclude = ['experiment', 'outcome', 'publication', 'note']


class EAVOutcomeForm(forms.ModelForm):

    class Meta:
        model = EAV
        exclude = ['experiment', 'population', 'publication', 'note']


class EAVPublicationForm(forms.ModelForm):

    class Meta:
        model = EAV
        exclude = ['experiment', 'outcome', 'population', 'note']
