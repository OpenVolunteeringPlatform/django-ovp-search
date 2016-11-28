from django.conf.urls import url, include
from rest_framework import routers
from ovp_search import views


project_search = routers.DefaultRouter()
project_search.register(r'projects', views.ProjectSearchResource, 'search-projects')

organization_search = routers.DefaultRouter()
organization_search.register(r'organizations', views.OrganizationSearchResource, 'search-organizations')

urlpatterns = [
  url(r'^search/', include(project_search.urls)),
  url(r'^search/', include(organization_search.urls)),
  url(r'^search/country-cities/(?P<country>[^/]+)/', views.query_country, name='search-query-country'),
]
