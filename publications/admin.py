from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from mptt.admin import DraggableMPTTAdmin
from .models import Profile, User  # AbstractUser with email address as username
from .models import Subject, Publication, Assessment, Intervention, Population, Outcome, Design, Experiment, Crop, ExperimentDesign, ExperimentCrop, ExperimentPopulation, ExperimentLatLong, ExperimentPopulationOutcome


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

admin.site.register(Subject)

admin.site.register(Publication)
admin.site.register(Assessment)
admin.site.register(Population)
admin.site.register(Design)
admin.site.register(Experiment)
admin.site.register(Crop)

# Intersection tables
admin.site.register(ExperimentDesign)
admin.site.register(ExperimentCrop)
admin.site.register(ExperimentPopulation)
admin.site.register(ExperimentPopulationOutcome)
admin.site.register(ExperimentLatLong)

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
