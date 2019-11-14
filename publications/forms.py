from django import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import NON_FIELD_ERRORS
from django.forms.widgets import NumberInput
from ast import literal_eval
from mptt.forms import TreeNodeChoiceField
from .models import Assessment, Attribute, Coordinates, Data, Date, EAV, Experiment, ExperimentDesign, ExperimentPopulation, ExperimentPopulationOutcome, Intervention, Outcome, Profile, Publication, PublicationPopulation, PublicationPopulationOutcome, Study, User, UserSubject, XCountry


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


class UserSubjectForm(forms.ModelForm):

    class Meta:
        model = UserSubject
        fields = ['user_for_comparison']


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
        fields = ['cannot_find', 'cannot_access', 'language_barrier', 'secondary_literature',
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
        widgets = {
            'location': forms.TextInput(attrs={
                'placeholder': "e.g., 'along two rivers in Germany' or 'in an irrigated maize field in the Ebro River valley, Spain'"
            }),
            'methods': forms.Textarea(attrs={
                'placeholder': "e.g., 'Herbicide (glyphosate) was sprayed on four treatment plots but not on four control plots. Plots were 2 x 2 meters.'"
            })
        }


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


class StudyForm(forms.ModelForm):
    study_id = forms.IntegerField(min_value=1)

    class Meta:
        model = Study
        fields = ['study_id', 'study_name']


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
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "The names of co-variates must be unique. Please use a different name for this covariate.",
            }
        }

    def clean_attribute(self):
        data = self.cleaned_data['attribute']
        reserved_attributes = [
            # Terms that are used in the api_query_string of the Shiny app, which could cause conflicts with URL bookmarking inputs
            "bookmark", "country", "intervention", "outcome", "publication", "refresh", "subject", "user",
            # Terms that are used as column names in the Shiny app, which could cause conflicts
            "citation", "population", "comparison", "study_id", "study_name",
            "note", "treatment_mean", "treatment_sd", "treatment_n", "treatment_se",
            "control_mean", "control_sd", "control_n", "control_se", "n", "unit",
            "lsd", "is_significant", "approximate_p_value", "p_value", "z_value",
            "correlation_coefficient", "effect_size", "effect_size_unit",
            "other_effect_size_unit", "lower_limit", "upper_limit", "confidence",
            "se", "variance", "methods", "location", "design",
            "treatment_sd_from_se", "control_sd_from_se", "lower_is_better",
            "response_ratio", "log_response_ratio", "v_from_sd_and_n",
            "mean_difference", "significance_from_lsd", "selected_significance",
            "p_from_significance", "selected_p", "z_from_p", "selected_z",
            "v_from_z", "selected_v", "study", "es_and_v", "selected_v_mads"
        ]
        for attribute in reserved_attributes:
            if attribute.upper() == data.upper():
                raise forms.ValidationError("This name is reserved. Please use a different name.")
        return data

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


class KappaForm(forms.Form):
    user_1 = forms.ModelChoiceField(queryset=User.objects.all())
    user_2 = forms.ModelChoiceField(queryset=User.objects.all())
    percent = forms.FloatField(widget=NumberInput(attrs={'id': 'percent', 'value': '10', 'min': '0', 'max': '100', 'step': '0.5'}))
    number = forms.IntegerField(widget=NumberInput(attrs={'id': 'number', 'value': '10', 'min': '0'}))
    intervention = TreeNodeChoiceField(queryset=Intervention.objects.all().get_descendants(include_self=True), level_indicator = "---")
    outcome = TreeNodeChoiceField(queryset=Outcome.objects.all().get_descendants(include_self=True), level_indicator = "---")
