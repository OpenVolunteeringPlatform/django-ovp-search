from django.core.exceptions import PermissionDenied

from ovp_projects.serializers.project import ProjectSearchSerializer
from ovp_projects.models import Project

from ovp_organizations.models import Organization
from ovp_organizations.serializers import OrganizationSearchSerializer

from ovp_users.models.user import User
from ovp_users.serializers.user import get_user_search_serializer

from ovp_search import helpers
from ovp_search import filters

from django.core.cache import cache

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import response
from rest_framework import decorators

from haystack.query import SearchQuerySet, SQ


class OrganizationSearchResource(mixins.ListModelMixin, viewsets.GenericViewSet):
  serializer_class = OrganizationSearchSerializer

  def get_queryset(self):
    params = self.request.GET

    key = 'organizations-{}'.format(hash(frozenset(params.items())))
    cache_ttl = 120
    result = cache.get(key)

    if not result:
      highlighted = params.get('highlighted') == 'true'
      query = params.get('query', None)
      cause = params.get('cause', '')
      address = params.get('address', None)
      name = params.get('name', None)
      published = params.get('published', 'true')

      queryset = SearchQuerySet().models(Organization)
      queryset = queryset.filter(highlighted=True) if highlighted else queryset
      queryset = queryset.filter(content=query) if query else queryset
      queryset = filters.by_published(queryset, published)
      queryset = filters.by_address(queryset, address)
      queryset = filters.by_name(queryset, name)
      queryset = filters.by_causes(queryset, cause)


      # haystack SearchQuerySet has to be converted to a django QuerySet
      # to work properly with django-rest-framework
      # TODO: Find a solution
      result_keys = [q.pk for q in queryset]
      result = Organization.objects.filter(pk__in=result_keys, deleted=False).prefetch_related('causes').select_related('address').order_by('-highlighted')
      cache.set(key, result, cache_ttl)

    return result


class ProjectSearchResource(mixins.ListModelMixin, viewsets.GenericViewSet):
  serializer_class = ProjectSearchSerializer

  def get_queryset(self):
    params = self.request.GET

    key = 'projects-{}'.format(hash(frozenset(params.items())))
    cache_ttl = 120
    result = cache.get(key)

    if not result:
      query = params.get('query', None)
      cause = params.get('cause', None)
      skill = params.get('skill', None)
      address = params.get('address', None)
      highlighted = (params.get('highlighted') == 'true')
      name = params.get('name', None)
      published = params.get('published', 'true')

      queryset = SearchQuerySet().models(Project)
      queryset = queryset.filter(highlighted=True) if highlighted else queryset
      queryset = queryset.filter(content=query) if query else queryset
      queryset = filters.by_published(queryset, published)
      queryset = filters.by_address(queryset, address, project=True)
      queryset = filters.by_name(queryset, name)
      queryset = filters.by_skills(queryset, skill)
      queryset = filters.by_causes(queryset, cause)

      # Get order attributes
      ordered = ''
      if 'ordered' in params:
        if params['ordered'] == 'desc':
          ordered = '-'

      order_by_field = params['order_by'] if 'order_by' in params else 'highlighted'

      result_keys = [q.pk for q in queryset]
      result = Project.objects.filter(pk__in=result_keys, deleted=False, closed=False).prefetch_related('skills', 'causes').select_related('address', 'owner').order_by(ordered + order_by_field)
      cache.set(key, result, cache_ttl)

    return result


class UserSearchResource(mixins.ListModelMixin, viewsets.GenericViewSet):
  serializer_class = get_user_search_serializer()

  def __init__(self, *args, **kwargs):
    self.check_user_search_enabled()
    return super(UserSearchResource, self).__init__(*args, **kwargs)

  def check_user_search_enabled(self):
    s = helpers.get_settings()
    if not s.get('ENABLE_USER_SEARCH', False):
      raise PermissionDenied

  def get_queryset(self):
    params = self.request.GET
    key = 'users-{}'.format(hash(frozenset(params.items())))
    cache_ttl = 120
    result = cache.get(key)

    if not result:
      cause = params.get('cause', None)
      skill = params.get('skill', None)

      queryset = SearchQuerySet().models(User)
      queryset = filters.by_skills(queryset, skill)
      queryset = filters.by_causes(queryset, cause)

      result_keys = [q.pk for q in queryset]
      result = User.objects.filter(pk__in=result_keys, profile__public=True).prefetch_related('profile__skills', 'profile__causes')
      cache.set(key, result, cache_ttl)

    return result


@decorators.api_view(["GET"])
def query_country(request, country):
  available_cities = []

  search_term = helpers.whoosh_raw("{}-country".format(country))
  queryset = SearchQuerySet().models(Project).filter(address_components__exact=search_term)

  for project in queryset:
    for comp in project.address_components:
      if "-administrative_area_level_2" in comp or "-locality" in comp:
        city_name = comp.replace("-administrative_area_level_2", "").replace("-locality", "")
        if city_name not in available_cities:
          available_cities.append(city_name)

  available_cities.sort()

  return response.Response(available_cities)
