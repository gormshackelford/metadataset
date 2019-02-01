from .models import Country, Design, Experiment, ExperimentCountry, ExperimentDesign, ExperimentPopulation, ExperimentPopulationOutcome, Intervention, Outcome, Publication, Subject
from rest_framework import serializers


class CountrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Country
        fields = ('country', 'url')


class DesignSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Design
        fields = ('design', 'url')


class InterventionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Intervention
        fields = ('intervention', 'url')


class OutcomeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Outcome
        fields = ('outcome', 'url')


class PublicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Publication
        fields = ('title', 'id')


class SubjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subject
        fields = ('subject', 'url')


class ExperimentCountrySerializer(serializers.HyperlinkedModelSerializer):
    country = serializers.SlugRelatedField(slug_field='country', read_only=True)

    class Meta:
        model = ExperimentCountry
        fields = ('country', )


class ExperimentDesignSerializer(serializers.HyperlinkedModelSerializer):
    design = serializers.SlugRelatedField(slug_field='design', read_only=True)

    class Meta:
        model = ExperimentDesign
        fields = ('design', )


class ExperimentSerializer(serializers.HyperlinkedModelSerializer):
    intervention = InterventionSerializer(read_only=True)
    publication = PublicationSerializer(read_only=True)
    experiment_countries = ExperimentCountrySerializer(many=True, read_only=True)
    experiment_designs = ExperimentDesignSerializer(many=True, read_only=True)

    class Meta:
        model = Experiment
        fields = ('intervention', 'publication', 'experiment_countries', 'experiment_designs', 'url')


class ExperimentPopulationSerializer(serializers.HyperlinkedModelSerializer):
    experiment = ExperimentSerializer(read_only=True)
    population = OutcomeSerializer(read_only=True)

    class Meta:
        model = ExperimentPopulation
        fields = ('experiment', 'population')


class ExperimentPopulationOutcomeSerializer(serializers.HyperlinkedModelSerializer):
    experiment_population = ExperimentPopulationSerializer(read_only=True)
    outcome = OutcomeSerializer(read_only=True)

    class Meta:
        model = ExperimentPopulationOutcome
        exclude = ('created', )
