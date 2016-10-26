from ovp_projects import serializers
from ovp_projects import models

from django.core.cache import cache

from rest_framework import generics

from haystack.query import SearchQuerySet

class ProjectList(generics.ListAPIView):
  serializer_class = serializers.ProjectSearchSerializer

  def get_queryset(self):
    params = self.request.GET

    #nonprofit = params.get('nonprofit', None)

    key = 'projects-{}'.format(hash(frozenset(params.items())))
    cache_ttl = 120
    result = cache.get(key)

    # Do not cache nonprofit results
    if not result or nonprofit:
      query = params.get('query', None)
      cause = params.get('cause', None)
      skill = params.get('skill', None)
      address = params.get('address', None)
      highlighted = (params.get('highlighted') == 'true')

      queryset = SearchQuerySet().models(models.Project)

      #if nonprofit:
      #  nonprofit = Nonprofit.objects.get(user__slug=nonprofit)
      #  queryset = queryset.filter(nonprofit=nonprofit)

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

                  if component_type == u"colloquial_area":
                    search_region = type_string

                  if type_string not in types:
                    types.append(type_string)

            # Filter all address components
            if not search_region:
              for address_type in types:
                queryset = queryset.filter(address_components=address_type)

            # User is filtering for Grande São Paulo
            # We have to hack our way around it
            else:
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
      result = models.Project.objects.filter(pk__in=result_keys, deleted=False, published=True, closed=False).prefetch_related('skills', 'causes', 'work__availabilities').select_related('job', 'work', 'address').order_by('-highlighted')

      cache.set(key, result, cache_ttl)

    return result
