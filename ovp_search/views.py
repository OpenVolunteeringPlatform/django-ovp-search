from ovp_projects.serializers.project import ProjectSearchSerializer
from ovp_projects.models import Project
from ovp_organizations.models import Organization

from ovp_organizations.serializers import OrganizationSearchSerializer

from ovp_search import helpers

from django.core.cache import cache

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import response
from rest_framework import decorators

from haystack.query import SearchQuerySet, SQ

import json


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
      cause = params.get('cause', None)
      address = params.get('address', None)
      name = params.get('name', None)
      published = params.get('published', 'true')

      queryset = SearchQuerySet().models(Organization)

      if published == "true":
        queryset = queryset.filter(published=True)
      elif published == "false":
        queryset = queryset.filter(published=False)
      # Any other value will return both published and unpublished

      if name:
        queryset = queryset.filter(name=name)

      if address:
        address = json.loads(address)
        types = []
        search_region = False

        if u'address_components' in address:
          for component in address[u'address_components']:
            for component_type in component[u'types']:
              if not search_region:
                type_string = u"{}-{}".format(component[u'long_name'], component_type).strip()

                if component_type == u"colloquial_area": # pragma: no cover
                  raise Exception("to be implemented/tested")
                  search_region = type_string

                if type_string not in types:
                  types.append(type_string)

          # Filter all address components
          if not search_region:
            for address_type in types:
              queryset = queryset.filter(address_components=helpers.whoosh_raw(address_type))

          # User is filtering for Grande São Paulo
          # We have to hack our way around it
          else: # pragma: no cover
            raise Exception("to be implemented/tested")
            filters = GoogleRegion.objects.filter(region_name=search_region)
            keys = [f.filter_by for f in filters]
            queryset = queryset.filter(address_components__in=keys)


      queryset = queryset.filter(highlighted=True) if highlighted else queryset
      queryset = queryset.filter(content=query) if query else queryset

      if cause:
        causes = cause.split(',')
        q_obj = SQ()
        for c in causes:
          q_obj.add(SQ(causes=c), SQ.OR)
        queryset = queryset.filter(q_obj)

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

    # TODO: Implement when Organization has slug
    #nonprofit = params.get('nonprofit', None)

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

      if published == "true":
        queryset = queryset.filter(published=True)
      elif published == "false":
        queryset = queryset.filter(published=False)
      # Any other value will return both published and unpublished

      # TODO: Implement when Organization has slug
      #if nonprofit:
      #  nonprofit = Nonprofit.objects.get(user__slug=nonprofit)
      #  queryset = queryset.filter(nonprofit=nonprofit)

      if name:
        queryset = queryset.filter(name=name)

      if address:
        address = json.loads(address)

        if u'address_components' in address:
          types = []
          search_region = False

          if len(address[u'address_components']): #filtrar endereço
            for component in address[u'address_components']:
              for component_type in component[u'types']:
                if not search_region:
                  type_string = u"{}-{}".format(component[u'long_name'], component_type).strip()

                  if component_type == u"colloquial_area": # pragma: no cover
                    search_region = type_string

                  if type_string not in types:
                    types.append(type_string)

            # Filter all address components
            if not search_region:
              for address_type in types:
                queryset = queryset.filter(address_components=helpers.whoosh_raw(address_type))

            # User is filtering for Grande São Paulo
            # We have to hack our way around it
            else: # pragma: no cover
              raise Exception("to be implemented/tested")
              filters = GoogleRegion.objects.filter(region_name=search_region)
              keys = [f.filter_by for f in filters]
              queryset = queryset.filter(address_components__in=keys)
          else: # remotos
            queryset = queryset.filter(can_be_done_remotely=True)


      queryset = queryset.filter(highlighted=True) if highlighted else queryset
      queryset = queryset.filter(content=query) if query else queryset

      if skill:
        skills = skill.split(',')
        q_obj = SQ()
        for s in skills:
          q_obj.add(SQ(skills=s), SQ.OR)
        queryset = queryset.filter(q_obj)

      if cause:
        causes = cause.split(',')
        q_obj = SQ()
        for c in causes:
          q_obj.add(SQ(causes=c), SQ.OR)
        queryset = queryset.filter(q_obj)

      # haystack SearchQuerySet has to be converted to a django QuerySet
      # to work properly with django-rest-framework
      # TODO: Find a solution
      result_keys = [q.pk for q in queryset]
      result = Project.objects.filter(pk__in=result_keys, deleted=False, closed=False).prefetch_related('skills', 'causes').select_related('address', 'owner').order_by('-highlighted')
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
