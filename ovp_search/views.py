from django.core.exceptions import PermissionDenied

from ovp_projects.serializers.project import ProjectSearchSerializer
from ovp_projects.models import Project

from ovp_organizations.models import Organization
from ovp_organizations.serializers import OrganizationSearchSerializer

from ovp_users.models.user import User
from ovp_users.serializers.user import get_user_search_serializer
from ovp_users.models.profile import get_profile_model, UserProfile

from ovp_search import helpers
from ovp_search import filters

from django.core.cache import cache

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import response
from rest_framework import decorators
from rest_framework import pagination

from haystack.query import SearchQuerySet, SQ


class DefaultSearchPagination(pagination.PageNumberPagination):
  page_size = 20
  page_size_query_param = 'page_size'
  max_page_size = 30

class OrganizationSearchResource(mixins.ListModelMixin, viewsets.GenericViewSet):
  serializer_class = OrganizationSearchSerializer
  filter_backends = (filters.OrderingFilter,)
  ordering_fields = ('slug', 'name', 'website', 'facebook_page', 'details', 'description', 'type', 'hidden_address')

  pagination_class = DefaultSearchPagination

  def get_queryset(self):
    params = self.request.GET

    key = 'organizations-{}'.format(hash(frozenset(params.items())))
    cache_ttl = 120
    result = cache.get(key)

    if not result:
      highlighted = params.get('highlighted') == 'true'
      published = params.get('published', 'true')

      query = params.get('query', None)
      cause = params.get('cause', None)
      address = params.get('address', None)
      name = params.get('name', None)

      queryset = SearchQuerySet().models(Organization)
      queryset = queryset.filter(highlighted=1) if highlighted else queryset
      queryset = queryset.filter(content=query) if query else queryset
      queryset = filters.by_name(queryset, name) if name else queryset
      queryset = filters.by_published(queryset, published)
      queryset = filters.by_address(queryset, address) if address else queryset
      queryset = filters.by_causes(queryset, cause) if cause else queryset

      result_keys = [q.pk for q in queryset]
      result = Organization.objects.filter(pk__in=result_keys, deleted=False).prefetch_related('causes').select_related('address').order_by('-highlighted')
      result = filters.filter_out(result, "ORGANIZATIONS")
      cache.set(key, result, cache_ttl)

    return result


class ProjectSearchResource(mixins.ListModelMixin, viewsets.GenericViewSet):
  serializer_class = ProjectSearchSerializer
  filter_backends = (filters.ProjectRelevanceOrderingFilter,)
  ordering_fields = ('name', 'slug', 'details', 'description', 'highlighted', 'published_date', 'created_date', 'max_applies', 'minimum_age', 'hidden_address', 'crowdfunding', 'public_project', 'relevance', 'closed', 'job__end_date')

  pagination_class = DefaultSearchPagination

  def get_base_queryset(self, pks = None, closed_clause=None):
    base_queryset = Project.objects.filter(deleted=False)
    # if closed_clause is None:
    closed_clause = helpers.get_settings('OVP_PROJECTS').get('DEFAULT_INCLUDE_CLOSED', None)
    base_queryset = base_queryset if closed_clause else base_queryset.filter(closed=False)
    if len(pks) > 0:
      return base_queryset.filter(pk__in=pks)

    return base_queryset.filter(pk__in=[])

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
      organization = params.get('organization', None)
      not_organization = params.get('not_organization', None)

      queryset = SearchQuerySet().models(Project)
      queryset = queryset.filter(highlighted=1) if highlighted else queryset
      queryset = queryset.filter(content=query) if query else queryset
      queryset = filters.by_published(queryset, published)
      queryset = filters.by_address(queryset, address, project=True)
      queryset = filters.by_name(queryset, name)
      queryset = filters.by_skills(queryset, skill)
      queryset = filters.by_causes(queryset, cause)

      result_keys = [q.pk for q in queryset]
      if not_organization:
        org = [o for o in not_organization.split(',')]
        result = self.get_base_queryset(result_keys).prefetch_related('skills', 'causes').select_related('address', 'owner').exclude(organization__in=org)
      elif organization:
        org = [o for o in organization.split(',')]
        result = self.get_base_queryset(result_keys).prefetch_related('skills', 'causes').select_related('address', 'owner').filter(organization__in=org)
      else:
        result = self.get_base_queryset(result_keys).prefetch_related('skills', 'causes').select_related('address', 'owner')

      result = filters.filter_out(result, "PROJECTS")
      cache.set(key, result, cache_ttl)

    return result


class UserSearchResource(mixins.ListModelMixin, viewsets.GenericViewSet):
  serializer_class = get_user_search_serializer()
  filter_backends = (filters.OrderingFilter,)
  ordering_fields = ('slug', 'name')

  pagination_class = DefaultSearchPagination

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
      name = params.get('name', None)

      queryset = SearchQuerySet().models(User)
      queryset = filters.by_skills(queryset, skill)
      queryset = filters.by_causes(queryset, cause)
      queryset = filters.by_name(queryset, name)

      result_keys = [q.pk for q in queryset]
      related_field_name = get_profile_model()._meta.get_field('user').related_query_name()

      result = User.objects.filter(pk__in=result_keys, public=True).prefetch_related(related_field_name + '__skills', related_field_name + '__causes').select_related(related_field_name)
      cache.set(key, result, cache_ttl)

    return result


@decorators.api_view(["GET"])
def query_country_deprecated(request, country):
  # Legacy/deprecated route
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


@decorators.api_view(["GET"])
def available_country_cities(request, country):
  key = "available-cities-{}".format(hash(country))
  cache_ttl = 120
  result = cache.get(key)

  if not result:
    result = {"projects": [], "organizations": [], "common": []}

    search_term = helpers.whoosh_raw("{}-country".format(country))

    queryset = SearchQuerySet().models(Project).filter(address_components__exact=search_term, published=1, closed=0)
    projects = helpers.get_cities(queryset)

    queryset = SearchQuerySet().models(Organization).filter(address_components__exact=search_term, published=1)
    organizations = helpers.get_cities(queryset)

    common = projects & organizations
    projects = projects - common
    organizations = organizations - common

    result["common"] = sorted(common)
    result["projects"] = sorted(projects)
    result["organizations"] = sorted(organizations)

    cache.set(key, result, cache_ttl)

  return response.Response(result)
