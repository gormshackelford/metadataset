from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_publication, name='add_publication'),
    path('publication/<int:publication_pk>/', views.publication, name='publication'),
    path('publication/<int:publication_pk>/intervention/<int:experiment_index>/', views.experiment, name='experiment'),
    path('publication/<int:publication_pk>/intervention/<int:experiment_index>/population/<int:population_index>/', views.population, name='population')
]
