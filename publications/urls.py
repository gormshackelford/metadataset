from django.urls import path, re_path
from django.conf import settings  # For django-debug-toolbar
from django.conf.urls import include  # For django-debug-toolbar
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('signup/', views.signup, name='signup'),
    path('email_sent/', views.email_sent, name='email_sent'),
    path('email_confirmed/', views.email_confirmed, name='email_confirmed'),
    path('email_not_confirmed/', views.email_not_confirmed, name='email_not_confirmed'),
    re_path('confirm_email/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', views.confirm_email, name='confirm_email'),
    path('add/', views.add_publication, name='add_publication'),
    path('publication/<int:publication_pk>/', views.publication, name='publication'),
    path('publication/<int:publication_pk>/intervention/<int:experiment_index>/', views.experiment, name='experiment'),
    path('publication/<int:publication_pk>/intervention/<int:experiment_index>/population/<int:population_index>/', views.population, name='population'),
    path('publication/<int:publication_pk>/intervention/<int:experiment_index>/population/<int:population_index>/outcome/<int:outcome_index>/', views.outcome, name='outcome')
]

if settings.DEBUG:
   import debug_toolbar
   urlpatterns += [
       path('__debug__/', include(debug_toolbar.urls)),
   ]
