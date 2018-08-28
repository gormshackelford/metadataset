from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from urllib.parse import quote_plus
from ast import literal_eval
import itertools


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model with email address as username."""

    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return '{email}'.format(email=self.email)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_is_confirmed = models.BooleanField(default=False)
    institution = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return 'Profile for {email}'.format(email=self.user.email)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


# Subjects for systematic reviews (as "subject-wide evidence syntheses")
class Subject(models.Model):
    subject = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, blank=True)
    text = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.subject = self.subject.lower()
        max_length = 255  # For MySQL, unique/indexed fields must be < 256.
        self.slug = slugify(self.subject)[:max_length]
        # Check if this slug exists. If it exists, add a hyphen and a number and repeat until the slug is unique.
        for counter in itertools.count(1):
            if not Subject.objects.filter(slug=self.slug).exists():
                break
            # Add a hyphen and a number (minus the length of the hyphen and the counter, to maintain max_length).
            self.slug = "{slug}-{counter}".format(slug=self.slug[:max_length - len(str(counter)) - 1], counter=counter)

        super(Subject, self).save(*args, **kwargs)

    def __str__(self):
        return self.subject


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
    note = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def google_string(self):
        string = quote_plus(self.title)
        return string

    @property
    def author_list(self):
        try:
            list = literal_eval(self.authors)
            return list
        # If the author field is not a Python list (e.g., ['Surname, A.B.', 'Surname, C.D.']) or cannot be displayed as a string, return None.
        except:
            list = None
            return list


# "Population" is the "P" in "PICO" (also referred to as "Patient" or "Problem"). The purpose of this database is to record the effect of an Intervention ("I") on a Population ("P"), measured in terms of an Outcome ("O"), with respect to a Control ("C"). Population is not a model in itself, but is the first level in the Outcome model.


# "Intervention" is the "I" in "PICO".
class Intervention(MPTTModel):
    intervention = models.CharField(max_length=255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255)
    code = models.CharField(max_length=30, null=True, blank=True)

    def save(self, *args, **kwargs):
        max_length = 255  # For MySQL, unique/indexed fields must be < 256.
        self.slug = slugify(self.intervention)[:max_length]
        # Check if this slug exists. If it exists, add a hyphen and a number and repeat until the slug is unique.
        for counter in itertools.count(1):
            if not Intervention.objects.filter(slug=self.slug).exists():
                break
            # Add a hyphen and a number (minus the length of the hyphen and the counter, to maintain max_length).
            self.slug = "{slug}-{counter}".format(slug=self.slug[:max_length - len(str(counter)) - 1], counter=counter)
        super(Intervention, self).save(*args, **kwargs)

    def __str__(self):
        return self.intervention

    class MPTTMeta:
        order_insertion_by = ['code']


# "Comparison" is the "C" in "PICO". It is a field in the model for effect sizes ("ExperimentPopulationOutcome").


# "Outcome" is the "O" in "PICO".
class Outcome(MPTTModel):
    outcome = models.CharField(max_length=255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255)
    code = models.CharField(max_length=30, null=True, blank=True)

    def save(self, *args, **kwargs):
        max_length = 255  # For MySQL, unique/indexed fields must be < 256.
        self.slug = slugify(self.outcome)[:max_length]
        # Check if this slug exists. If it exists, add a hyphen and a number and repeat until the slug is unique.
        for counter in itertools.count(1):
            if not Outcome.objects.filter(slug=self.slug).exists():
                break
            # Add a hyphen and a number (minus the length of the hyphen and the counter, to maintain max_length).
            self.slug = "{slug}-{counter}".format(slug=self.slug[:max_length - len(str(counter)) - 1], counter=counter)
        super(Outcome, self).save(*args, **kwargs)

    def __str__(self):
        return self.outcome

    class MPTTMeta:
        order_insertion_by = ['code']


class Crop(MPTTModel):
    crop = models.CharField(max_length=255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255)

    def save(self, *args, **kwargs):
        max_length = 255  # For MySQL, unique/indexed fields must be < 256.
        self.slug = slugify(self.crop)[:max_length]
        # Check if this slug exists. If it exists, add a hyphen and a number and repeat until the slug is unique.
        for counter in itertools.count(1):
            if not Crop.objects.filter(slug=self.slug).exists():
                break
            # Add a hyphen and a number (minus the length of the hyphen and the counter, to maintain max_length).
            self.slug = "{slug}-{counter}".format(slug=self.slug[:max_length - len(str(counter)) - 1], counter=counter)
        super(Crop, self).save(*args, **kwargs)

    def __str__(self):
        return self.crop

    def get_absolute_url(self):
        return reverse('filter_by_crop', kwargs={'path': self.get_path()})

    class MPTTMeta:
        order_insertion_by = ['crop']


# Experimental design (e.g., "replicated", "randomized", "controlled")
class Design(models.Model):
    design = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.design


class Country(models.Model):
    country = models.CharField(max_length=255)
    un_m49 = models.IntegerField(blank=True, null=True)
    iso_alpha_3 = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return self.country

    class Meta:
        verbose_name_plural = "countries"


# Intersection tables

# The country in which the experiments were done (not necessarily the country of the publication authors)
class PublicationCountry(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.publication.title

    class Meta:
        verbose_name_plural = "publication countries"


# The lat/long at which the experiments were done
class PublicationLatLong(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    latitude = models.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    longitude = models.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.publication.title


# The date on which the experiments were done (not the date of publication)
class PublicationDate(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    year = models.IntegerField(blank=True, null=True)
    MONTH_CHOICES = (
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December")
    )
    month = models.IntegerField(blank=True, null=True, choices=MONTH_CHOICES)
    DAY_CHOICES = tuple((x,x) for x in range(1,32))
    day = models.IntegerField(choices=DAY_CHOICES, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.publication.title


class PublicationPopulation(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    population = models.ForeignKey(Outcome, blank=True, null=True, on_delete=models.CASCADE)  # Populations are the first level in the classification of outcomes.
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.publication.title


class PublicationPopulationOutcome(models.Model):
    publication_population = models.ForeignKey(PublicationPopulation, on_delete=models.CASCADE)
    outcome = models.ForeignKey(Outcome, blank=True, null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.publication_population.publication.title


# We define one "experment" (i.e. one "study") as one "intervention" that is described in one "publication". We use the "PICO" terminology for describing experiments ("P" = "Population", "I" = "Intervention", "C" = "Comparison", and "O" = "Outcome"). In our data model, one experiment can have multiple "populations" and one "population" can have multiple "outcomes" (e.g., effects of intercropping [intervention] on crop yield [population = crop; outcome = crop yield] and soil nutrients [population = soil; outcome = soil nitrogen; outcome = soil phosphorus]).
class Experiment(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, blank=True, null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.publication.title


# This and other intersection tables that begin with "Experiment" apply to only one experiment in a publication, whereas those that begin with "Publication" (e.g., "PublicationCountry") apply to all experiments within a publication.
class ExperimentCountry(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.experiment.publication.title

    class Meta:
        verbose_name_plural = "experiment countries"


class ExperimentCrop(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.experiment.publication.title


class ExperimentDesign(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    design = models.ForeignKey(Design, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.experiment.publication.title


class ExperimentLatLong(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    latitude = models.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    longitude = models.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.experiment.publication.title


class ExperimentDate(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    year = models.IntegerField(blank=True, null=True)
    MONTH_CHOICES = (
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December")
    )
    month = models.IntegerField(blank=True, null=True, choices=MONTH_CHOICES)
    DAY_CHOICES = tuple((x,x) for x in range(1,32))
    day = models.IntegerField(choices=DAY_CHOICES, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.experiment.publication.title


class ExperimentPopulation(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    population = models.ForeignKey(Outcome, blank=True, null=True, on_delete=models.CASCADE)  # Populations are the first level in the classification of outcomes.
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.experiment.publication.title


class ExperimentPopulationOutcome(models.Model):
    experiment_population = models.ForeignKey(ExperimentPopulation, on_delete=models.CASCADE)
    outcome = TreeForeignKey(Outcome, on_delete=models.CASCADE)
    comparison = models.TextField(blank=True, null=True)  # "Comparison" is the "C" in "PICO".
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
        ("Other", "Other")
    )
    effect_size_unit = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        choices=EFFECT_SIZE_UNIT_CHOICES
    )
    other_effect_size_unit = models.CharField(max_length=60, blank=True, null=True)
    lower_limit = models.FloatField(blank=True, null=True, help_text="Lower limit of the confidence interval for the effect size")
    upper_limit = models.FloatField(blank=True, null=True, help_text="Upper limit of the confidence interval for the effect size")
    confidence = models.FloatField(blank=True, null=True,  validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="Confidence of the confidence interval (percent)")
    se = models.FloatField(blank=True, null=True, help_text="Standard error of the effect size")
    variance = models.FloatField(blank=True, null=True, help_text="Variance of the effect size")
    n = models.IntegerField(blank=True, null=True, help_text="Number of replicates")
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
        max_length=30,
        blank=True,
        null=True,
        choices=APPROXIMATE_P_VALUE_CHOICES
    )
    exact_p_value = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(1)], help_text="Please enter a value from 0 to 1.")
    z_value = models.FloatField(blank=True, null=True)
    treatment_mean = models.IntegerField(blank=True, null=True)
    control_mean = models.IntegerField(blank=True, null=True)
    unit = models.CharField(max_length=60, blank=True, null=True)
    n_treatment = models.IntegerField(blank=True, null=True)
    n_control = models.IntegerField(blank=True, null=True)
    sd_treatment = models.FloatField(blank=True, null=True)
    sd_control = models.FloatField(blank=True, null=True)
    se_treatment = models.FloatField(blank=True, null=True)
    se_control = models.FloatField(blank=True, null=True)
    sed = models.FloatField(blank=True, null=True, help_text="Standard error of the difference between the means")
    lsd = models.FloatField(blank=True, null=True, help_text="Least significant difference between the means")
    note = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.experiment_population.experiment.publication.title


class Assessment(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    is_relevant = models.BooleanField()
    is_completed = models.BooleanField(default=False)
    full_text_is_relevant = models.NullBooleanField()
    note = models.TextField(blank=True, null=True)
    cannot_find = models.BooleanField(default=False)
    cannot_access = models.BooleanField(default=False)
    secondary_literature = models.BooleanField(default=False)
    no_population = models.BooleanField(default=False)
    no_intervention = models.BooleanField(default=False)
    no_outcome = models.BooleanField(default=False)
    no_comparator = models.BooleanField(default=False)
    other = models.BooleanField(default=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return '{boolean}: "{publication}" is relevant to "{subject}"'.format(
            boolean=self.is_relevant, publication=self.publication,
            subject=self.subject
        )


class AssessmentStatus(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment_order = models.TextField()
    next_assessment = models.IntegerField(blank=True, null=True)
    previous_full_text_assessment = models.IntegerField(blank=True, null=True)
    completed_assessments = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Progress report for "{user}" and subject "{subject}"'.format(user=self.user.email, subject=self.subject)

    class Meta:
        verbose_name_plural = "assessment statuses"
