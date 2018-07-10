from django import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from mptt.forms import TreeNodeChoiceField
from .models import Assessment, Publication, Intervention, Experiment, ExperimentCountry, ExperimentCrop, ExperimentDate, ExperimentDesign, ExperimentLatLong, ExperimentPopulation, ExperimentPopulationOutcome, Profile, User


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
        exclude = []


class ProfileForm(forms.ModelForm):
    institution = forms.CharField(max_length=255)

    class Meta:
        model = Profile
        exclude = []


class AssessmentForm(forms.ModelForm):

    class Meta:
        model = Assessment
        fields = []


class FullTextAssessmentForm(forms.ModelForm):

    class Meta:
        model = Assessment
        fields = ['note']


class PublicationForm(forms.ModelForm):

    class Meta:
        model = Publication
        exclude = ['abstract', 'subject']


class ExperimentForm(forms.ModelForm):

    class Meta:
        model = Experiment
        exclude = ['publication', 'user']


class ExperimentCountryForm(forms.ModelForm):

    class Meta:
        model = ExperimentCountry
        exclude = ['experiment']


class ExperimentCropForm(forms.ModelForm):

    class Meta:
        model = ExperimentCrop
        exclude = ['experiment']


class ExperimentDateForm(forms.ModelForm):

    class Meta:
        model = ExperimentDate
        exclude = ['experiment']


class ExperimentDesignForm(forms.ModelForm):

    class Meta:
        model = ExperimentDesign
        exclude = ['experiment']


class ExperimentLatLongForm(forms.ModelForm):
    latitude = forms.FloatField(min_value=-90.0, max_value=90.0)
    longitude = forms.FloatField(min_value=-180.0, max_value=180.0)

    class Meta:
        model = ExperimentLatLong
        exclude = ['experiment']


class ExperimentPopulationForm(forms.ModelForm):

    class Meta:
        model = ExperimentPopulation
        exclude = ['experiment', 'old_population']


class ExperimentPopulationOutcomeForm(forms.ModelForm):

    class Meta:
        model = ExperimentPopulationOutcome
        fields = ['outcome']


class EffectForm(forms.ModelForm):

    class Meta:
        model = ExperimentPopulationOutcome
        exclude = ['experiment_population', 'outcome']
