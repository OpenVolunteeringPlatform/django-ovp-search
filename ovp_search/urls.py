from django.conf.urls import url, include
from ovp_search import views

urlpatterns = [
  url(r'projects/search', views.ProjectList.as_view(), name='projects-list'),
]
