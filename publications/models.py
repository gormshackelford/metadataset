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

INTENTIONCHOICES = (('mitigate impacts of invasive population','Mitigate impacts of invasive population'), ('eradicate invasive population','Eradicate invasive population'), 
                  ('prevent spread of invasive population','Prevent spread of invasive population'), ('multiple aims','Multiple aims'), ('study aim unclear','Study aim unclear'))


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


class Intervention(MPTTModel):
    intervention = models.CharField(max_length=255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, blank=True)
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


class Outcome(MPTTModel):
    outcome = models.CharField(max_length=255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, blank=True)
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
    slug = models.SlugField(max_length=255, blank=True)

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


class Country(models.Model):
    country = models.CharField(max_length=255)
    un_m49 = models.IntegerField(blank=True, null=True)
    iso_alpha_3 = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return self.country

    class Meta:
        verbose_name_plural = "countries"


# Experimental design (e.g., "replicated", "randomized", "controlled")
class Design(MPTTModel):
    design = models.CharField(max_length=60)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        max_length = 255  # For MySQL, unique/indexed fields must be < 256.
        self.slug = slugify(self.design)[:max_length]
        # Check if this slug exists. If it exists, add a hyphen and a number and repeat until the slug is unique.
        for counter in itertools.count(1):
            if not Design.objects.filter(slug=self.slug).exists():
                break
            # Add a hyphen and a number (minus the length of the hyphen and the counter, to maintain max_length).
            self.slug = "{slug}-{counter}".format(slug=self.slug[:max_length - len(str(counter)) - 1], counter=counter)
        super(Design, self).save(*args, **kwargs)

    def __str__(self):
        return self.design

    class MPTTMeta:
        order_insertion_by = ['design']


# Attributes for the entity-attribute-value (EAV) model
class Attribute(MPTTModel):
    attribute = models.CharField(max_length=255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, blank=True)
    TYPE_FACTOR = 'factor'
    TYPE_NUMBER = 'number'
    TYPE_CHOICES = (
        (TYPE_FACTOR, 'Factor'),
        (TYPE_NUMBER, 'Number')
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    unit = models.CharField(max_length=30, blank=True)
    note = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        max_length = 255  # For MySQL, unique/indexed fields must be < 256.
        self.slug = slugify(self.attribute)[:max_length]
        # Check if this slug exists. If it exists, add a hyphen and a number and repeat until the slug is unique.
        for counter in itertools.count(1):
            if not Attribute.objects.filter(slug=self.slug).exists():
                break
            # Add a hyphen and a number (minus the length of the hyphen and the counter, to maintain max_length).
            self.slug = "{slug}-{counter}".format(slug=self.slug[:max_length - len(str(counter)) - 1], counter=counter)
        super(Attribute, self).save(*args, **kwargs)

    def __str__(self):
        return self.attribute

    class Meta:
        unique_together = ('attribute', 'parent')
        ordering = ['attribute']

    class MPTTMeta:
        order_insertion_by = ['attribute']


# Subjects for systematic reviews (as "subject-wide evidence syntheses")
class Subject(MPTTModel):
    subject = models.CharField(max_length=255, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, blank=True, null=True, on_delete=models.SET_NULL)  # The root node for this subject in the tree of interventions (each subject can have its own classification of interventions)
    outcome = models.ForeignKey(Outcome, blank=True, null=True, on_delete=models.SET_NULL)  # The root node for this subject in the tree of outcomes (each subject can have its own classification of outcomes)
    design = models.ForeignKey(Design, blank=True, null=True, on_delete=models.SET_NULL)  # The root node for this subject in the tree of designs (each subject can have its own classification of designs)
    attribute = models.ForeignKey(Attribute, blank=True, null=True, on_delete=models.SET_NULL)  # The root node for this subject in the tree of attributes (each subject can have its own classification of attributes)
    slug = models.SlugField(max_length=255, blank=True)
    text = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    data_are_public = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.subject = self.subject.lower()
        max_length = 255  # For MySQL, unique/indexed fields must be < 256.
        self.slug = slugify(self.subject)[:max_length]

        super(Subject, self).save(*args, **kwargs)

    def __str__(self):
        return self.subject

    class MPTTMeta:
        order_insertion_by = ['subject']


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
    citation = models.CharField(max_length=60, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
    is_from_systematic_search = models.BooleanField(default=True)
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


# Intersection tables


# The subjects that a user has permission to work on
class UserSubject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    can_edit_attributes = models.BooleanField(default=True)
    user_for_comparison = models.ForeignKey(User, related_name="user_subject_user_for_comparison", blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.email


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


# We define one "experment" as one "intervention" that is described in one
# "publication". We use the "PICO" terminology for describing experiments ("P" =
# "Population", "I" = "Intervention", "C" = "Comparison", and "O" = "Outcome").
# In our data model, one experiment can have multiple "populations" and one
# "population" can have multiple "outcomes" (e.g., effects of intercropping
# [intervention] on crop yield [population = crop; outcome = crop yield] and
# soil nutrients [population = soil; outcome = soil nitrogen; outcome = soil
# phosphorus]).
class Experiment(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, blank=True, null=True, on_delete=models.CASCADE)
    location = models.CharField(max_length=255, blank=True, null=True)
    methods = models.TextField(blank=True, null=True)
    shortresults = models.TextField(blank=True,null=True)
    longresults = models.TextField(blank=True,null=True)
    studyintention = models.CharField(max_length=255, choices=INTENTIONCHOICES, default = INTENTIONCHOICES[0])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.publication.title


class ExperimentPopulation(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    population = models.ForeignKey(Outcome, on_delete=models.CASCADE)  # Populations are level 1 in the classification of outcomes.
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.experiment.publication.title


class ExperimentPopulationOutcome(models.Model):
    experiment_population = models.ForeignKey(ExperimentPopulation, on_delete=models.CASCADE)
    outcome = TreeForeignKey(Outcome, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.experiment_population.experiment.publication.title


class ExperimentDesign(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    design = models.ForeignKey(Design, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.experiment.publication.title


class Coordinates(models.Model):
    # Entity options (only one of these should be non-null per instance)
    publication = models.ForeignKey(Publication, related_name="coordinates_publication", blank=True, null=True, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, related_name="coordinates_experiment", blank=True, null=True, on_delete=models.CASCADE)
    population = models.ForeignKey(ExperimentPopulation, related_name="coordinates_population", blank=True, null=True, on_delete=models.CASCADE)
    outcome = models.ForeignKey(ExperimentPopulationOutcome, related_name="coordinates_outcome", blank=True, null=True, on_delete=models.CASCADE)
    # End of entity options
    latitude_degrees = models.FloatField(null=True, blank=True, default=None, validators=[MinValueValidator(0.0), MaxValueValidator(90.0)])
    latitude_minutes = models.FloatField(null=True, blank=True, default=None, validators=[MinValueValidator(0.0), MaxValueValidator(60.0)])
    latitude_seconds = models.FloatField(null=True, blank=True, default=None, validators=[MinValueValidator(0.0), MaxValueValidator(60.0)])
    LATITUDE_DIRECTIONS = (
        ("N", "N (+)"),
        ("S", "S (-)")
    )
    latitude_direction = models.CharField(max_length=10, blank=True, null=True, choices=LATITUDE_DIRECTIONS, default="N")
    longitude_degrees = models.FloatField(null=True, blank=True, default=None, validators=[MinValueValidator(0.0), MaxValueValidator(180.0)])
    longitude_minutes = models.FloatField(null=True, blank=True, default=None, validators=[MinValueValidator(0.0), MaxValueValidator(60.0)])
    longitude_seconds = models.FloatField(null=True, blank=True, default=None, validators=[MinValueValidator(0.0), MaxValueValidator(60.0)])
    LONGITUDE_DIRECTIONS = (
        ("E", "E (+)"),
        ("W", "W (-)")
    )
    longitude_direction = models.CharField(max_length=10, blank=True, null=True, choices=LONGITUDE_DIRECTIONS, default="E")
    # Indexes: these allow for distinct() queries at multiple levels in the
    # hierarchy, while allowing for instances to be created at only one level in
    # the hierarchy (i.e. for only one of the "entity options" above).
    publication_index = models.ForeignKey(Publication, related_name="coordinates_publication_index", blank=True, null=True, on_delete=models.CASCADE)
    experiment_index = models.ForeignKey(Experiment, related_name="coordinates_experiment_index", blank=True, null=True, on_delete=models.CASCADE)
    population_index = models.ForeignKey(ExperimentPopulation, related_name="coordinates_population_index", blank=True, null=True, on_delete=models.CASCADE)
    outcome_index = models.ForeignKey(ExperimentPopulationOutcome, related_name="coordinates_outcome_index", blank=True, null=True, on_delete=models.CASCADE)
    # End of indexes
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "{pk}".format(pk=self.pk)

    class Meta:
        verbose_name_plural = "coordinates"


class Date(models.Model):
    # Entity options (only one of these should be non-null per instance)
    publication = models.ForeignKey(Publication, related_name="date_publication", blank=True, null=True, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, related_name="date_experiment", blank=True, null=True, on_delete=models.CASCADE)
    population = models.ForeignKey(ExperimentPopulation, related_name="date_population", blank=True, null=True, on_delete=models.CASCADE)
    outcome = models.ForeignKey(ExperimentPopulationOutcome, related_name="date_outcome", blank=True, null=True, on_delete=models.CASCADE)
    # End of entity options
    start_year = models.IntegerField(blank=True, null=True)
    end_year = models.IntegerField(blank=True, null=True)
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
    start_month = models.IntegerField(blank=True, null=True, choices=MONTH_CHOICES)
    end_month = models.IntegerField(blank=True, null=True, choices=MONTH_CHOICES)
    DAY_CHOICES = tuple((x,x) for x in range(1,32))
    start_day = models.IntegerField(choices=DAY_CHOICES, blank=True, null=True)
    end_day = models.IntegerField(choices=DAY_CHOICES, blank=True, null=True)
    # Indexes: these allow for distinct() queries at multiple levels in the
    # hierarchy, while allowing for instances to be created at only one level in
    # the hierarchy (i.e. for only one of the "entity options" above).
    publication_index = models.ForeignKey(Publication, related_name="date_publication_index", blank=True, null=True, on_delete=models.CASCADE)
    experiment_index = models.ForeignKey(Experiment, related_name="date_experiment_index", blank=True, null=True, on_delete=models.CASCADE)
    population_index = models.ForeignKey(ExperimentPopulation, related_name="date_population_index", blank=True, null=True, on_delete=models.CASCADE)
    outcome_index = models.ForeignKey(ExperimentPopulationOutcome, related_name="date_outcome_index", blank=True, null=True, on_delete=models.CASCADE)
    # End of indexes
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "{pk}".format(pk=self.pk)


class Study(models.Model):
    # Entity options (only one of these should be non-null per instance)
    publication = models.ForeignKey(Publication, related_name="study_publication", blank=True, null=True, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, related_name="study_experiment", blank=True, null=True, on_delete=models.CASCADE)
    population = models.ForeignKey(ExperimentPopulation, related_name="study_population", blank=True, null=True, on_delete=models.CASCADE)
    outcome = models.ForeignKey(ExperimentPopulationOutcome, related_name="study_outcome", blank=True, null=True, on_delete=models.CASCADE)
    # End of entity options
    study_id = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    study_name = models.CharField(max_length=60, blank=True, null=True)
    # Indexes: these allow for distinct() queries at multiple levels in the
    # hierarchy, while allowing for instances to be created at only one level in
    # the hierarchy (i.e. for only one of the "entity options" above).
    publication_index = models.ForeignKey(Publication, related_name="study_publication_index", blank=True, null=True, on_delete=models.CASCADE)
    experiment_index = models.ForeignKey(Experiment, related_name="study_experiment_index", blank=True, null=True, on_delete=models.CASCADE)
    population_index = models.ForeignKey(ExperimentPopulation, related_name="study_population_index", blank=True, null=True, on_delete=models.CASCADE)
    outcome_index = models.ForeignKey(ExperimentPopulationOutcome, related_name="study_outcome_index", blank=True, null=True, on_delete=models.CASCADE)
    # End of indexes
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "{pk}".format(pk=self.pk)


class XCountry(models.Model):
    # Entity options (only one of these should be non-null per instance)
    publication = models.ForeignKey(Publication, related_name="xcountry_publication", blank=True, null=True, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, related_name="xcountry_experiment", blank=True, null=True, on_delete=models.CASCADE)
    population = models.ForeignKey(ExperimentPopulation, related_name="xcountry_population", blank=True, null=True, on_delete=models.CASCADE)
    outcome = models.ForeignKey(ExperimentPopulationOutcome, related_name="xcountry_outcome", blank=True, null=True, on_delete=models.CASCADE)
    # End of entity options
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    # Indexes: these allow for distinct() queries at multiple levels in the
    # hierarchy, while allowing for instances to be created at only one level in
    # the hierarchy (i.e. for only one of the "entity options" above).
    publication_index = models.ForeignKey(Publication, related_name="xcountry_publication_index", blank=True, null=True, on_delete=models.CASCADE)
    experiment_index = models.ForeignKey(Experiment, related_name="xcountry_experiment_index", blank=True, null=True, on_delete=models.CASCADE)
    population_index = models.ForeignKey(ExperimentPopulation, related_name="xcountry_population_index", blank=True, null=True, on_delete=models.CASCADE)
    outcome_index = models.ForeignKey(ExperimentPopulationOutcome, related_name="xcountry_outcome_index", blank=True, null=True, on_delete=models.CASCADE)
    # End of indexes
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "{pk}".format(pk=self.pk)

    class Meta:
        verbose_name_plural = "xcountries"


class Data(models.Model):
    comparison = models.CharField(max_length=255, blank=True, null=True)  # "Comparison" is the "C" in "PICO".
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    experiment_population = models.ForeignKey(ExperimentPopulation, on_delete=models.CASCADE)
    experiment_population_outcome = models.ForeignKey(ExperimentPopulationOutcome, on_delete=models.CASCADE)
    treatment_mean = models.FloatField(blank=True, null=True)
    treatment_mean_before = models.FloatField(blank=True, null=True)
    treatment_sd = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    treatment_sd_before = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    treatment_n = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    treatment_n_before = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    treatment_se = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    treatment_se_before = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    control_mean = models.FloatField(blank=True, null=True)
    control_mean_before = models.FloatField(blank=True, null=True)
    control_sd = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    control_sd_before = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    control_n = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    control_n_before = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    control_se = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    control_se_before = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    n = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=60, blank=True, null=True)
    lsd = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    IS_SIGNIFICANT_CHOICES = (
        (None, "---------"),
        (True, "Yes"),
        (False, "No")
    )
    is_significant = models.NullBooleanField(choices=IS_SIGNIFICANT_CHOICES)
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
    p_value = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    z_value = models.FloatField(blank=True, null=True)
    correlation_coefficient = models.FloatField(blank=True, null=True, validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    effect_size = models.FloatField(blank=True, null=True, help_text="As published, not as calculated from the data above")
    EFFECT_SIZE_UNIT_CHOICES = (
        ("d", "Standardized mean difference (d)"),
        ("R", "Response ratio (R)"),
        ("L", "Log response ratio (L)"),
        ("r", "Pearson correlation coefficient (r)"),
        ("Zr", "Fischer's Z-transformed r (Zr)"),
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
    confidence = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    se = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    variance = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    note = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.experiment_population_outcome.experiment_population.experiment.publication.title


class EAV(models.Model):
    """
    This is an entity-attribute-value (EAV) model, and the entity can be
    recorded at different levels (publication, experiment, experiment_population,
    experiment_population_outcome). Note that these different levels are related
    to one another hierarchically (publication > experiment >
    experiment_population > experiment_population_outcome).
    """
    # E: Entity options (only one of these should be non-null per instance)
    publication = models.ForeignKey(Publication, related_name="EAV_publication", blank=True, null=True, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, related_name="EAV_experiment", blank=True, null=True, on_delete=models.CASCADE)
    population = models.ForeignKey(ExperimentPopulation, related_name="EAV_population", blank=True, null=True, on_delete=models.CASCADE)
    outcome = models.ForeignKey(ExperimentPopulationOutcome, related_name="EAV_outcome", blank=True, null=True, on_delete=models.CASCADE)
    # End of entity options
    # A: Attribute
    attribute = models.ForeignKey(Attribute, related_name="EAV_attribute", on_delete=models.CASCADE)
    # V: Value options (only one of these should be non-null per instance)
    value_as_number = models.FloatField(blank=True, null=True)
    value_as_factor = models.ForeignKey(Attribute, related_name="EAV_value_as_factor", blank=True, null=True, on_delete=models.CASCADE)
    # End of value options
    note = models.CharField(max_length=255, blank=True, null=True)
    # Indexes: these allow for distinct() queries at multiple levels in the
    # hierarchy, while allowing for instances to be created at only one level in
    # the hierarchy (i.e. for only one of the "entity options" above).
    publication_index = models.ForeignKey(Publication, related_name="EAV_publication_index", blank=True, null=True, on_delete=models.CASCADE)
    experiment_index = models.ForeignKey(Experiment, related_name="EAV_experiment_index", blank=True, null=True, on_delete=models.CASCADE)
    population_index = models.ForeignKey(ExperimentPopulation, related_name="EAV_population_index", blank=True, null=True, on_delete=models.CASCADE)
    outcome_index = models.ForeignKey(ExperimentPopulationOutcome, related_name="EAV_outcome_index", blank=True, null=True, on_delete=models.CASCADE)
    # End of indexes
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.attribute.attribute

    class Meta:
        unique_together = (('attribute', 'user', 'publication'), ('attribute', 'user', 'experiment'), ('attribute', 'user', 'population'), ('attribute', 'user', 'outcome'))


#TODO: Build an interface for saving the results of analyses from the Shiny app, which will use this model.
class Analysis(models.Model):
    effect_size = models.FloatField(null=True, blank=True)
    pval = models.FloatField(null=True, blank=True)
    lb = models.FloatField(null=True, blank=True)
    ub = models.FloatField(null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE)
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE)
    api_query_string = models.CharField(max_length=255)
    shiny_bookmark = models.CharField(max_length=255)
    user_settings = models.CharField(max_length=60)
    there_was_an_error = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Subject: {subject}; Intervention: {intervention}; Outcome: {outcome}; Query: {api_query_string}; Settings: {user_settings}; Bookmark: {shiny_bookmark}".format(subject=self.subject.pk, intervention=self.intervention.pk, outcome=self.outcome.pk, api_query_string=self.api_query_string, user_settings=self.user_settings, shiny_bookmark=self.shiny_bookmark)

    class Meta:
        verbose_name_plural = "analyses"


class Assessment(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    is_relevant = models.BooleanField()
    is_completed = models.BooleanField(default=False)
    full_text_is_relevant = models.NullBooleanField()
    note = models.TextField(blank=True, null=True)
    cannot_find = models.BooleanField(default=False)
    cannot_access = models.BooleanField(default=False)
    language_barrier = models.BooleanField(default=False)
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
