from django import forms
from django.db import models
from .models import Publication, Experiment, ExperimentCrop, ExperimentDesign, ExperimentIUCNThreat, ExperimentLatLong, ExperimentPopulation, ExperimentPopulationOutcome


class PublicationForm(forms.ModelForm):

    class Meta:
        model = Publication
        exclude = []


class ExperimentForm(forms.ModelForm):

    class Meta:
        model = Experiment
        exclude = ['publication']


class ExperimentCropForm(forms.ModelForm):

    class Meta:
        model = ExperimentCrop
        exclude = ['experiment']


class ExperimentDesignForm(forms.ModelForm):

    class Meta:
        model = ExperimentDesign
        exclude = ['experiment']


class ExperimentIUCNThreatForm(forms.ModelForm):

    class Meta:
        model = ExperimentIUCNThreat
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
        exclude = ['experiment']


class ExperimentPopulationOutcomeForm(forms.ModelForm):
    exact_p_value = forms.FloatField(min_value=0, max_value=1, help_text="Please enter a value from 0 to 1.", required=False)

    class Meta:
        model = ExperimentPopulationOutcome
        exclude = ['experiment_population']
