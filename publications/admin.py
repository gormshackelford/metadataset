from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from mptt.admin import DraggableMPTTAdmin
from reversion.admin import VersionAdmin
from .models import Profile, User  # AbstractUser with email address as username
from .models import Assessment, AssessmentStatus, Attribute, EAV, Coordinates, Country, Crop, Data, Design, Experiment, ExperimentCountry, ExperimentCrop, ExperimentDate, ExperimentDesign, ExperimentPopulation, ExperimentLatLong, ExperimentPopulationOutcome, Intervention, Outcome, Publication, PublicationCountry, PublicationDate, PublicationLatLong, PublicationLatLongDMS, PublicationPopulation, PublicationPopulationOutcome, Subject, UserSubject


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


admin.site.register(Country)
admin.site.register(Crop)
admin.site.register(Profile)
admin.site.register(UserSubject)


# Admin for models with version control (django-reversion)
@admin.register(Publication)
class PublicationAdmin(VersionAdmin):
    pass


# Admin for models with readonly fields (created and updated)
class AssessmentAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(Assessment, AssessmentAdmin)

class AssessmentStatusAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(AssessmentStatus, AssessmentStatusAdmin)

class CoordinatesAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(Coordinates, CoordinatesAdmin)

class DataAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(Data, DataAdmin)

class EAVAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(EAV, EAVAdmin)

class ExperimentAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(Experiment, ExperimentAdmin)

class ExperimentDesignAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(ExperimentDesign, ExperimentDesignAdmin)

class ExperimentCountryAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(ExperimentCountry, ExperimentCountryAdmin)

class ExperimentCropAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(ExperimentCrop, ExperimentCropAdmin)

class ExperimentPopulationAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(ExperimentPopulation, ExperimentPopulationAdmin)

class ExperimentPopulationOutcomeAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(ExperimentPopulationOutcome, ExperimentPopulationOutcomeAdmin)

class ExperimentLatLongAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(ExperimentLatLong, ExperimentLatLongAdmin)

class ExperimentDateAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(ExperimentDate, ExperimentDateAdmin)

class PublicationCountryAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(PublicationCountry, PublicationCountryAdmin)

class PublicationDateAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(PublicationDate, PublicationDateAdmin)

class PublicationLatLongAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(PublicationLatLong, PublicationLatLongAdmin)

class PublicationLatLongDMSAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(PublicationLatLongDMS, PublicationLatLongDMSAdmin)

class PublicationPopulationOutcomeAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(PublicationPopulationOutcome, PublicationPopulationOutcomeAdmin)

class PublicationPopulationAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(PublicationPopulation, PublicationPopulationAdmin)


# Admin for hierarchical models (django-mptt)
admin.site.register(
    Attribute,
    DraggableMPTTAdmin,
    list_display=(
        'tree_actions',
        'indented_title',
    ),
    list_display_links=(
        'indented_title',
    ),
)

admin.site.register(
    Design,
    DraggableMPTTAdmin,
    list_display=(
        'tree_actions',
        'indented_title',
    ),
    list_display_links=(
        'indented_title',
    ),
)

admin.site.register(
    Intervention,
    DraggableMPTTAdmin,
    list_display=(
        'tree_actions',
        'indented_title',
    ),
    list_display_links=(
        'indented_title',
    ),
)

admin.site.register(
    Outcome,
    DraggableMPTTAdmin,
    list_display=(
        'tree_actions',
        'indented_title',
    ),
    list_display_links=(
        'indented_title',
    ),
)

admin.site.register(
    Subject,
    DraggableMPTTAdmin,
    list_display=(
        'tree_actions',
        'indented_title',
    ),
    list_display_links=(
        'indented_title',
    ),
)
