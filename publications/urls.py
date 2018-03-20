from django.urls import path, re_path
from django.conf import settings  # For django-debug-toolbar
from django.conf.urls import include  # For django-debug-toolbar
from . import views
from .models import Intervention, Outcome
import mptt_urls


urlpatterns = [
    path('', views.home, name='home'),
    path('browse', views.browse, name='browse'),
    path('about', views.about, name='about'),
    path('methods', views.methods, name='methods'),
    path('signup/', views.signup, name='signup'),
    path('contact/', views.contact, name='contact'),
    path('publications/', views.publications, name='publications'),
    path('email_sent/', views.email_sent, name='email_sent'),
    path('email_confirmed/', views.email_confirmed, name='email_confirmed'),
    path('email_not_confirmed/', views.email_not_confirmed, name='email_not_confirmed'),
    re_path('confirm_email/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', views.confirm_email, name='confirm_email'),
    path('publication/<int:publication_pk>/', views.publication, name='publication'),
    path('publication/<int:publication_pk>/intervention/<int:experiment_index>/', views.experiment, name='experiment'),
    path('publication/<int:publication_pk>/intervention/<int:experiment_index>/population/<int:population_index>/', views.population, name='population'),
    path('publication/<int:publication_pk>/intervention/<int:experiment_index>/population/<int:population_index>/outcome/<int:outcome_index>/', views.outcome, name='outcome'),
    re_path('filter/intervention/(?P<path>.*)', mptt_urls.view(model=Intervention, view=views.filter_by_intervention, slug_field='slug'), name='filter_by_intervention'),
    re_path('filter/outcome/(?P<path>.*)', mptt_urls.view(model=Outcome, view=views.filter_by_outcome, slug_field='slug'), name='filter_by_outcome')
]

if settings.DEBUG:
   import debug_toolbar
   urlpatterns += [
       path('__debug__/', include(debug_toolbar.urls)),
   ]
