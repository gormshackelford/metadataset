from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from mptt.admin import DraggableMPTTAdmin
from .models import Profile, User  # AbstractUser with email address as username
from .models import Subject, Publication, Assessment, AssessmentStatus, Intervention, Population, Outcome, Design, Experiment, Country, Crop, ExperimentCountry, ExperimentCrop, ExperimentDesign, ExperimentPopulation, ExperimentLatLong, ExperimentPopulationOutcome


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


admin.site.register(Profile)

admin.site.register(Country)
admin.site.register(Crop)
admin.site.register(Design)
admin.site.register(Population)
admin.site.register(Publication)

class ExperimentAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(Experiment, ExperimentAdmin)
class SubjectAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(Subject, SubjectAdmin)

# Intersection tables
class AssessmentAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(Assessment, AssessmentAdmin)
class AssessmentStatusAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
admin.site.register(AssessmentStatus, AssessmentStatusAdmin)
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

# DraggableMPTTAdmin for hierarchical models
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
