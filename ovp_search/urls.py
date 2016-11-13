from django.conf.urls import url, include
from rest_framework import routers
from ovp_search import views


router = routers.DefaultRouter()
router.register(r'search', views.SearchResource, 'search-list')


urlpatterns = [
  url(r'^', include(router.urls)),
]
