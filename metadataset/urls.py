"""metadataset URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from publications import views


router = routers.DefaultRouter()
router.register(r'attributes', views.AttributeViewSet)
router.register(r'countries', views.CountryViewSet)
router.register(r'data', views.DataViewSet)
router.register(r'designs', views.DesignViewSet)
router.register(r'EAVs', views.EAVViewSet)
router.register(r'experiments', views.ExperimentViewSet)
router.register(r'experiment_designs', views.ExperimentDesignViewSet)
router.register(r'experiment_populations', views.ExperimentPopulationViewSet)
router.register(r'experiment_population_outcomes', views.ExperimentPopulationOutcomeViewSet)
router.register(r'interventions', views.InterventionViewSet)
router.register(r'outcomes', views.OutcomeViewSet)
router.register(r'publications', views.PublicationViewSet)
router.register(r'publication_populations', views.PublicationPopulationViewSet)
router.register(r'publication_population_outcomes', views.PublicationPopulationOutcomeViewSet)
router.register(r'subjects', views.SubjectViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('', include('publications.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
