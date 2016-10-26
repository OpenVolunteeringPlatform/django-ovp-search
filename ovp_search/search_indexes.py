from haystack import indexes
from ovp_projects.models import Project, Work, Job

class ProjectIndex(indexes.SearchIndex, indexes.Indexable):
  text = indexes.CharField(document=True, use_template=True)
  causes = indexes.MultiValueField(faceted=True)
  skills = indexes.MultiValueField(faceted=True)
  highlighted = indexes.BooleanField(model_attr='highlighted')
  can_be_done_remotely = indexes.BooleanField(faceted=True)
  published = indexes.BooleanField(model_attr='published')
  deleted = indexes.BooleanField(model_attr='deleted')
  closed = indexes.BooleanField(model_attr='closed')
  address_components = indexes.MultiValueField(faceted=True)

  def prepare_causes(self, obj):
    return [cause.id for cause in obj.causes.all()]

  def prepare_skills(self, obj):
    return [skill.id for skill in obj.skills.all()]

  def prepare_address_components(self, obj):
    types = []
    if obj.address:
      for component in obj.address.address_components.all():
        for component_type in component.types.all():
          types.append(u'{}-{}'.format(component.long_name, component_type.name))

    return types

  def prepare_can_be_done_remotely(self, obj):
    can_be_done_remotely = False

    # Try to get info from work object
    # Need to catch exceptions here because Work has a Project
    try:
      can_be_done_remotely = obj.work.can_be_done_remotely
    except Work.DoesNotExist:
      pass

    # Try to get info from job object
    # Need to catch exceptions here because Job has a Project
    try:
      can_be_done_remotely = obj.job.can_be_done_remotely
    except Job.DoesNotExist:
      pass

    return can_be_done_remotely


  def get_model(self):
    return Project

  def index_queryset(self, using=None):
    return self.get_model().objects.filter(closed=False, published=True, deleted=False)
