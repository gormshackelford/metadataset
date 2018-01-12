from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from urllib.parse import quote_plus


class Publication(models.Model):
    title = models.CharField(max_length=510)
    abstract = models.TextField(blank=True)
    authors = models.TextField(blank=True)
    year = models.CharField(max_length=30, blank=True)
    journal = models.CharField(max_length=510, blank=True)
    volume = models.CharField(max_length=30, blank=True)
    issue = models.CharField(max_length=30, blank=True)
    pages = models.CharField(max_length=30, blank=True)
    doi = models.CharField(max_length=510, blank=True)
    url = models.CharField(max_length=510, blank=True)
    publisher = models.CharField(max_length=510, blank=True)
    place = models.CharField(max_length=510, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def google_string(self):
        string = quote_plus(self.title)
        return string


# "Population" is the "P" in "PICO" (also referred to as "Patient" or "Problem"). The purpose of this database is to record the effect of an Intervention ("I") on a Population ("P"), measured in terms of an Outcome ("O"), with respect to a Control ("C").
class Population(models.Model):
    population = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.population


# "Intervention" is the "I" in "PICO".
class Intervention(models.Model):
    intervention = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.intervention


# "Comparison" is the "C" in "PICO".
class Comparison(models.Model):
    comparison = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.outcome


# "Outcome" is the "O" in "PICO".
class Outcome(models.Model):
    outcome = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.outcome


# Experimental design (e.g., "replicated", "randomized", "controlled")
class Design(models.Model):
    design = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.design


class Crop(models.Model):
    crop = models.CharField(max_length=126, unique=True)

    def __str__(self):
        return self.crop


# "Broad categories" from www.conservationevidence.com
class BroadCategory(models.Model):
    category = models.CharField(max_length=126, unique=True)

    def __str__(self):
        return self.category


class Taxon(models.Model):
    order = models.CharField(max_length=126)
    family = models.CharField(max_length=126)
    genus = models.CharField(max_length=126)
    species = models.CharField(max_length=126)

    def __str__(self):
        return self.genus


class IUCNActionLevel1(models.Model):
    action = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.action


class IUCNActionLevel2(models.Model):
    action = models.CharField(max_length=254)
    parent = models.ForeignKey(IUCNActionLevel1, on_delete=models.CASCADE)

    def __str__(self):
        return self.action


class IUCNActionLevel3(models.Model):
    action = models.CharField(max_length=254)
    parent = models.ForeignKey(IUCNActionLevel2, on_delete=models.CASCADE)

    def __str__(self):
        return self.action


class IUCNHabitatLevel1(models.Model):
    habitat = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.habitat


class IUCNHabitatLevel2(models.Model):
    habitat = models.CharField(max_length=254)
    parent = models.ForeignKey(IUCNHabitatLevel1, on_delete=models.CASCADE)

    def __str__(self):
        return self.habitat


class IUCNThreatLevel1(models.Model):
    threat = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.threat


class IUCNThreatLevel2(models.Model):
    threat = models.CharField(max_length=254)
    parent = models.ForeignKey(IUCNThreatLevel1, on_delete=models.CASCADE)

    def __str__(self):
        return self.threat


# Intersection tables

# We define an "experment" as one "intervention" that is described in one "publication". We use the "PICO" terminology for describing experiments ("P" = "Population", "I" = "Intervention", "C" = "Comparison", and "O" = "Outcome"). In our data model, one experiment can have multiple "populations" and one "population" can have multiple "outcomes" (e.g., effects of intercropping [intervention] on crop yield [population = crop; outcome = crop yield] and soil nutrients [population = soil; outcome = soil nitrogen; outcome = soil phosphorus]).
class Experiment(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE)

    def __str__(self):
        return self.publication.title


class ExperimentPopulation(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    population = models.ForeignKey(Population, on_delete=models.CASCADE)

    def __str__(self):
        return self.experiment.publication.title


class ExperimentDesign(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    design = models.ForeignKey(Design, on_delete=models.CASCADE)

    def __str__(self):
        return self.experiment.publication.title


class ExperimentCrop(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('experiment', 'crop')

    def __str__(self):
        return self.experiment.publication.title


class ExperimentTaxon(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    taxon = models.ForeignKey(Taxon, on_delete=models.CASCADE)

    def __str__(self):
        return self.experiment.publication.title


class ExperimentBroadCategory(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    broad_category = models.ForeignKey(BroadCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.experiment.publication.title


class ExperimentIUCNAction(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    action = models.ForeignKey(IUCNActionLevel3, on_delete=models.CASCADE)

    def __str__(self):
        return self.experiment.publication.title


class ExperimentIUCNHabitat(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    habitat = models.ForeignKey(IUCNHabitatLevel2, on_delete=models.CASCADE)

    def __str__(self):
        return self.experiment.publication.title


class ExperimentIUCNThreat(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    threat = models.ForeignKey(IUCNThreatLevel2, on_delete=models.CASCADE)

    def __str__(self):
        return self.experiment.publication.title


class ExperimentLatLong(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    latitude = models.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    longitude = models.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])

    def __str__(self):
        return self.experiment.publication.title


class ExperimentPopulationOutcome(models.Model):
    experiment_population = models.ForeignKey(ExperimentPopulation, on_delete=models.CASCADE)
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE)
    note = models.TextField(blank=True, null=True)
    EFFECT_CHOICES = (
        (1, "+"),
        (0, "0"),
        (-1, "-")
    )
    effect = models.IntegerField(
        blank=True,
        null=True,
        choices=EFFECT_CHOICES
    )
    effect_size = models.FloatField(blank=True, null=True)
    EFFECT_SIZE_UNIT_CHOICES = (
        ("g", "g - Hedges' g (standardized mean difference)"),
        ("R", "R - Response ratio"),
        ("L", "L - Log response ratio"),
        ("Zr", "Zr - Fischer's Z-transformed r"),
    )
    effect_size_unit = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        choices=EFFECT_SIZE_UNIT_CHOICES
    )
    other_unit = models.CharField(max_length=62, blank=True, null=True)
    sd = models.FloatField(blank=True, null=True)
    se = models.FloatField(blank=True, null=True)
    variance = models.FloatField(blank=True, null=True)
    n = models.IntegerField(blank=True, null=True)
    exact_p_value = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    APPROXIMATE_P_VALUE_CHOICES = (
        ("< 0.0001", "< 0.0001"),
        ("< 0.001", "< 0.001"),
        ("< 0.01", "< 0.01"),
        ("< 0.05", "< 0.05"),
        ("< 0.1", "< 0.1"),
        ("> 0.05", "> 0.05"),
        ("> 0.1", "> 0.1")
    )
    approximate_p_value = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        choices=APPROXIMATE_P_VALUE_CHOICES
    )
    z_value = models.FloatField(blank=True, null=True)
    significant = models.NullBooleanField(blank=True)
    treatment_mean = models.IntegerField(blank=True, null=True)
    control_mean = models.IntegerField(blank=True, null=True)
    unit = models.CharField(max_length=62, blank=True, null=True)
    n_treatment = models.IntegerField(blank=True, null=True)
    n_control = models.IntegerField(blank=True, null=True)
    sd_treatment = models.FloatField(blank=True, null=True)
    sd_control = models.FloatField(blank=True, null=True)
    se_treatment = models.FloatField(blank=True, null=True)
    se_control = models.FloatField(blank=True, null=True)
    sed = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.experiment_population.experiment.publication.title
