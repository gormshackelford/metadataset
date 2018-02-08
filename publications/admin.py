from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from .models import Profile, User  # AbstractUser with email address as username
from .models import Publication, Intervention, Population, Outcome, Design, Experiment, BroadCategory, Crop, Taxon, IUCNActionLevel1, IUCNActionLevel2, IUCNActionLevel3, IUCNHabitatLevel1, IUCNHabitatLevel2, IUCNThreatLevel1, IUCNThreatLevel2, ExperimentDesign, ExperimentBroadCategory, ExperimentCrop, ExperimentPopulation, ExperimentTaxon, ExperimentLatLong, ExperimentIUCNAction, ExperimentIUCNHabitat, ExperimentIUCNThreat, ExperimentPopulationOutcome


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

admin.site.register(Publication)
admin.site.register(Intervention)
admin.site.register(Population)
admin.site.register(Outcome)
admin.site.register(Design)
admin.site.register(Experiment)
admin.site.register(BroadCategory)
admin.site.register(Crop)
admin.site.register(Taxon)
admin.site.register(IUCNActionLevel1)
admin.site.register(IUCNActionLevel2)
admin.site.register(IUCNActionLevel3)
admin.site.register(IUCNHabitatLevel1)
admin.site.register(IUCNHabitatLevel2)
admin.site.register(IUCNThreatLevel1)
admin.site.register(IUCNThreatLevel2)

# Intersection tables
admin.site.register(ExperimentDesign)
admin.site.register(ExperimentBroadCategory)
admin.site.register(ExperimentCrop)
admin.site.register(ExperimentTaxon)
admin.site.register(ExperimentPopulation)
admin.site.register(ExperimentIUCNAction)
admin.site.register(ExperimentIUCNHabitat)
admin.site.register(ExperimentIUCNThreat)
admin.site.register(ExperimentLatLong)
admin.site.register(ExperimentPopulationOutcome)
