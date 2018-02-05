from django.urls import path
from django.conf import settings  # For django-debug-toolbar
from django.conf.urls import include  # For django-debug-toolbar
from . import views


urlpatterns = [
    path('', views.home, name='home'),
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
