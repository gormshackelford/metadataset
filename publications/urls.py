from django.urls import path, re_path
from django.conf import settings  # For django-debug-toolbar
from django.conf.urls import include  # For django-debug-toolbar
from . import views
from .models import Intervention, Outcome
import mptt_urls


urlpatterns = [
    path('', views.home, name='home'),
#    path('search/', include('haystack.urls')),
#    path('search/<subject>/', include('haystack.urls')),
    path('search/<subject>/', views.MySearchView.as_view(), name='haystack_search'),
    path('about/', views.about, name='about'),
    path('methods/', views.methods, name='methods'),
    path('notes/', views.notes, name='notes'),
    path('signup/', views.signup, name='signup'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('email_sent/', views.email_sent, name='email_sent'),
    path('email_confirmed/', views.email_confirmed, name='email_confirmed'),
    path('email_not_confirmed/', views.email_not_confirmed, name='email_not_confirmed'),
    re_path('confirm_email/(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', views.confirm_email, name='confirm_email'),
    path('subject/<subject>/', views.subject, name='subject'),
    path('subject/<subject>/attributes/', views.attributes, name='attributes'),
    path('subject/<subject>/attributes/<refresh>/', views.attributes, name='attributes'),
    path('subject/<subject>/attribute/<int:attribute_pk>/', views.attribute, name='attribute'),
    path('subject/<subject>/publications/', views.publications, name='publications'),
    path('subject/<subject>/publications/<state>/', views.publications, name='publications'),
    path('subject/<subject>/publications/<state>/download/<download>/', views.publications, name='publications'),
    path('subject/<subject>/publications/<state>/users/<users>/', views.publications, name='publications'),
    path('subject/<subject>/publications/<state>/users/<users>/download/<download>/', views.publications, name='publications'),
    path('subject/<subject>/kappa/', views.kappa, name='kappa'),

    # Filter publications

    # Filter by intervention
    path('subject/<subject>/publications/intervention/<int:intervention_pk>/', views.publications_x, name='publications_x'),
    # Filter by intervention and outcome
    path('subject/<subject>/publications/intervention/<int:intervention_pk>/outcome/<int:outcome_pk>/', views.publications_x, name='publications_x'),
    # Filter by intervention and outcome and country
    path('subject/<subject>/publications/intervention/<int:intervention_pk>/outcome/<int:outcome_pk>/<iso_a3>/', views.publications_x, name='publications_x'),
    # Filter by intervention and country (iso_a3)
    path('subject/<subject>/publications/intervention/<int:intervention_pk>/<iso_a3>/', views.publications_x, name='publications_x'),

    # Filter by outcome
    path('subject/<subject>/publications/outcome/<int:outcome_pk>/', views.publications_x, name='publications_x'),
    # Filter by outcome and country (iso_a3)
    path('subject/<subject>/publications/outcome/<int:outcome_pk>/<iso_a3>/', views.publications_x, name='publications_x'),

    # Filter by intervention
    path('subject/<subject>/intervention/<int:intervention_pk>/<state>/', views.this_intervention, name='this_intervention'),
    path('subject/<subject>/intervention/<int:intervention_pk>/<state>/<download>/', views.this_intervention, name='this_intervention'),
    # Filter by intervention and outcome
    path('subject/<subject>/intervention/<int:intervention_pk>/outcome/<int:outcome_pk>/<state>/', views.this_intervention, name='this_intervention'),
    path('subject/<subject>/intervention/<int:intervention_pk>/outcome/<int:outcome_pk>/<state>/<download>/', views.this_intervention, name='this_intervention'),
    # Filter by outcome
    path('subject/<subject>/outcome/<int:outcome_pk>/<state>/', views.this_outcome, name='this_outcome'),
    path('subject/<subject>/outcome/<int:outcome_pk>/<state>/<download>/', views.this_outcome, name='this_outcome'),
    # Filter by outcome and intervention
    path('subject/<subject>/outcome/<int:outcome_pk>/intervention/<int:intervention_pk>/<state>/', views.this_outcome, name='this_outcome'),
    path('subject/<subject>/outcome/<int:outcome_pk>/intervention/<int:intervention_pk>/<state>/<download>/', views.this_outcome, name='this_outcome'),

    path('subject/<subject>/browse-by-intervention/<state>/', views.browse_by_intervention, name='browse_by_intervention'),
    path('subject/<subject>/browse-by-intervention/<state>/<set>/', views.browse_by_intervention, name='browse_by_intervention'),
    path('subject/<subject>/browse-by-intervention/<state>/<set>/download/<download>/', views.browse_by_intervention, name='browse_by_intervention'),
    path('subject/<subject>/browse-by-outcome/<state>/', views.browse_by_outcome, name='browse_by_outcome'),
    path('subject/<subject>/browse-by-outcome/<state>/<set>/', views.browse_by_outcome, name='browse_by_outcome'),
    path('subject/<subject>/browse-by-outcome/<state>/<set>/download/<download>/', views.browse_by_outcome, name='browse_by_outcome'),
    path('subject/<subject>/add-publication/', views.add_publication, name='add_publication'),
    path('subject/<subject>/edit-publication/<int:publication_pk>/', views.edit_publication, name='edit_publication'),
    path('subject/<subject>/publication/<int:publication_pk>/', views.publication, name='publication'),
    path('subject/<subject>/publication/<int:publication_pk>/metadata/', views.metadata, name='metadata'),
    path('subject/<subject>/publication/<int:publication_pk>/population/<int:publication_population_index>/', views.publication_population, name='publication_population'),
    path('subject/<subject>/publication/<int:publication_pk>/intervention/<int:experiment_index>/', views.experiment, name='experiment'),
    path('subject/<subject>/publication/<int:publication_pk>/intervention/<int:experiment_index>/population/<int:population_index>/', views.population, name='population'),
    path('subject/<subject>/publication/<int:publication_pk>/intervention/<int:experiment_index>/population/<int:population_index>/outcome/<int:outcome_index>/', views.outcome, name='outcome'),
    path('subject/<subject>/full-text-navigation/<direction>/<state>/<users>/', views.full_text_navigation, name='full_text_navigation'),
    path('subject/<subject>/full-text-navigation/<direction>/<state>/<users>/<publication_pk>/', views.full_text_navigation, name='full_text_navigation'),
]

if settings.DEBUG:
   import debug_toolbar
   urlpatterns += [
       path('__debug__/', include(debug_toolbar.urls)),
   ]
