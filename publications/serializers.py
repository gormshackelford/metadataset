from .models import Attribute, Country, Data, Design, EAV, Experiment, ExperimentDesign, ExperimentPopulation, ExperimentPopulationOutcome, Intervention, Outcome, Publication, PublicationPopulation, PublicationPopulationOutcome, Subject, User, XCountry
from rest_framework import serializers


class AttributeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attribute
        exclude = ()


class CountrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Country
        exclude = ()


class DesignSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Design
        exclude = ()


class EAVSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EAV
        exclude = ()


class InterventionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Intervention
        exclude = ()


class OutcomeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Outcome
        exclude = ()


class PublicationSerializer(serializers.HyperlinkedModelSerializer):
    EAV_publication = EAVSerializer(many=True, read_only=True)  # Reverse foreign-key relationship (the default is the name of the model that has a foreign key to this model + "_set", unless a "related_name" is specified in that model, but that breaks other queries)

    class Meta:
        model = Publication
        exclude = ()


class SubjectSerializer(serializers.HyperlinkedModelSerializer):
    attribute = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Subject
        exclude = ()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', )


class XCountrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = XCountry
        exclude = ()


class ExperimentDesignSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ExperimentDesign
        exclude = ()


class ExperimentSerializer(serializers.HyperlinkedModelSerializer):
    EAV_experiment = EAVSerializer(many=True, read_only=True)  # Reverse foreign-key relationship (the default is the name of the model that has a foreign key to this model + "_set", unless a "related_name" is specified in that model, but that breaks other queries)
    xcountry_experiment_index = XCountrySerializer(many=True, read_only=True)  # Reverse foreign-key relationship (the default is the name of the model that has a foreign key to this model + "_set", unless a "related_name" is specified in that model, but that breaks other queries)
    experimentdesign_set = ExperimentDesignSerializer(many=True, read_only=True)  # Reverse foreign-key relationship (the default is the name of the model that has a foreign key to this model + "_set", unless a "related_name" is specified in that model, but that breaks other queries)
    class Meta:
        model = Experiment
        exclude = ()


class ExperimentPopulationSerializer(serializers.HyperlinkedModelSerializer):
    EAV_population = EAVSerializer(many=True, read_only=True)  # Reverse foreign-key relationship (the default is the name of the model that has a foreign key to this model + "_set", unless a "related_name" is specified in that model, but that breaks other queries)

    class Meta:
        model = ExperimentPopulation
        exclude = ()


class ExperimentPopulationOutcomeSerializer(serializers.HyperlinkedModelSerializer):
    experiment_population = ExperimentPopulationSerializer(read_only=True)
    outcome = OutcomeSerializer(read_only=True)
    EAV_outcome = EAVSerializer(many=True, read_only=True)  # Reverse foreign-key relationship (the default is the name of the model that has a foreign key to this model + "_set", unless a "related_name" is specified in that model, but that breaks other queries)

    class Meta:
        model = ExperimentPopulationOutcome
        exclude = ()


class PublicationPopulationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PublicationPopulation
        exclude = ()


class PublicationPopulationOutcomeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PublicationPopulationOutcome
        exclude = ()


class DataEAVSerializer(serializers.HyperlinkedModelSerializer):
    attribute = serializers.SlugRelatedField(slug_field='attribute', read_only=True)
    value_as_factor = serializers.SlugRelatedField(slug_field='attribute', read_only=True)

    class Meta:
        model = EAV
        fields = ('attribute', 'value_as_factor', 'value_as_number')


class DataXCountrySerializer(serializers.HyperlinkedModelSerializer):
    country = serializers.SlugRelatedField(slug_field='country', read_only=True)

    class Meta:
        model = XCountry
        fields = ('country', )


class DataExperimentDesignSerializer(serializers.HyperlinkedModelSerializer):
    design = serializers.SlugRelatedField(slug_field='design', read_only=True)

    class Meta:
        model = ExperimentDesign
        fields = ('design', )


class DataExperimentSerializer(serializers.HyperlinkedModelSerializer):
    intervention = serializers.SlugRelatedField(slug_field='intervention', read_only=True)
    EAV_experiment = DataEAVSerializer(many=True, read_only=True)  # Reverse foreign-key relationship (the default is the name of the model that has a foreign key to this model + "_set", unless a "related_name" is specified in that model, but that breaks other queries)
    experimentdesign_set = DataExperimentDesignSerializer(many=True, read_only=True)  # Reverse foreign-key relationship (the default is the name of the model that has a foreign key to this model + "_set", unless a "related_name" is specified in that model, but that breaks other queries)
    xcountry_experiment_index = DataXCountrySerializer(many=True, read_only=True)  # Reverse foreign-key relationship (the default is the name of the model that has a foreign key to this model + "_set", unless a "related_name" is specified in that model, but that breaks other queries)

    class Meta:
        model = Experiment
        exclude = ('created', 'updated', 'publication', 'url')


class DataExperimentPopulationSerializer(serializers.HyperlinkedModelSerializer):
    population = serializers.SlugRelatedField(slug_field='outcome', read_only=True)
    EAV_population = DataEAVSerializer(many=True, read_only=True)  # Reverse foreign-key relationship (the default is the name of the model that has a foreign key to this model + "_set", unless a "related_name" is specified in that model, but that breaks other queries)

    class Meta:
        model = ExperimentPopulation
        fields = ('population', 'EAV_population', )


class DataExperimentPopulationOutcomeSerializer(serializers.HyperlinkedModelSerializer):
    outcome = serializers.SlugRelatedField(slug_field='outcome', read_only=True)
    EAV_outcome = DataEAVSerializer(many=True, read_only=True)  # Reverse foreign-key relationship (the default is the name of the model that has a foreign key to this model + "_set", unless a "related_name" is specified in that model, but that breaks other queries)

    class Meta:
        model = ExperimentPopulationOutcome
        fields = ('outcome', 'EAV_outcome', )


class DataSerializer(serializers.HyperlinkedModelSerializer):
    publication = serializers.SlugRelatedField(slug_field='title', read_only=True)
    experiment = DataExperimentSerializer(read_only=True)
    experiment_population = DataExperimentPopulationSerializer(read_only=True)
    experiment_population_outcome = DataExperimentPopulationOutcomeSerializer(read_only=True)

    class Meta:
        model = Data
        exclude = ('subject', 'created', 'updated', 'url')
