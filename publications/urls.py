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
    path('systematic-review/<subject>/', views.subject, name='subject'),
    path('systematic-review/<subject>/publications', views.publications, name='publications'),
    path('systematic-review/<subject>/publications/<state>', views.publications, name='publications'),
    path('systematic-review/<subject>/publications/<state>/<download>', views.publications, name='publications'),
    path('systematic-review/<subject>/browse-by-intervention/', views.browse_by_intervention, name='browse_by_intervention'),
    path('systematic-review/<subject>/browse-by-outcome/', views.browse_by_outcome, name='browse_by_outcome'),
    path('systematic-review/<subject>/intervention/<int:intervention_pk>/', views.this_intervention, name='this_intervention'),
    path('systematic-review/<subject>/outcome/<int:outcome_pk>/', views.this_outcome, name='this_outcome'),
    path('systematic-review/<subject>/publications/intervention/<int:intervention_pk>/outcome/<int:outcome_pk>/', views.publications_x, name='publications_x'),
    path('about', views.about, name='about'),
    path('methods', views.methods, name='methods'),
    path('signup/', views.signup, name='signup'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('email_sent/', views.email_sent, name='email_sent'),
    path('email_confirmed/', views.email_confirmed, name='email_confirmed'),
    path('email_not_confirmed/', views.email_not_confirmed, name='email_not_confirmed'),
    re_path('confirm_email/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', views.confirm_email, name='confirm_email'),
    path('systematic-review/<subject>/edit-publication/<int:publication_pk>/', views.edit_publication, name='edit_publication'),
    path('systematic-review/<subject>/publication/<int:publication_pk>/', views.publication, name='publication'),
    path('systematic-review/<subject>/publication/<int:publication_pk>/metadata/', views.metadata, name='metadata'),
    path('systematic-review/<subject>/publication/<int:publication_pk>/population/<int:publication_population_index>/', views.publication_population, name='publication_population'),
    path('systematic-review/<subject>/publication/<int:publication_pk>/intervention/<int:experiment_index>/', views.experiment, name='experiment'),
    path('systematic-review/<subject>/publication/<int:publication_pk>/intervention/<int:experiment_index>/population/<int:population_index>/', views.population, name='population'),
    path('systematic-review/<subject>/publication/<int:publication_pk>/intervention/<int:experiment_index>/population/<int:population_index>/outcome/<int:outcome_index>/', views.outcome, name='outcome'),
    path('systematic-review/<subject>/full-text-navigation/<state>/', views.full_text_navigation, name='full_text_navigation'),
    path('systematic-review/<subject>/full-text-navigation/<state>/<publication_pk>/', views.full_text_navigation, name='full_text_navigation'),
]

if settings.DEBUG:
   import debug_toolbar
   urlpatterns += [
       path('__debug__/', include(debug_toolbar.urls)),
   ]
