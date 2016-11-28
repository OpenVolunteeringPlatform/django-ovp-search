from django.db import models
from haystack import signals

from ovp_projects.models import Project, Job, Work
from ovp_organizations.models import Organization
from ovp_core.models import GoogleAddress


class TiedModelRealtimeSignalProcessor(signals.BaseSignalProcessor):
  """
    TiedModelRealTimeSignalProcessor handles updates to a index tied to a model

    We need to be able to detect changes to a model a rebuild another index,
    such as detecting changes to GoogleAddress and updating the index
    for projects and organizations.

  """
  attach_to = [
    (Project, 'handle_save', 'handle_delete'),
    (Organization, 'handle_save', 'handle_delete'),
    (GoogleAddress, 'handle_address_save', 'handle_address_delete'),
    (Job, 'handle_job_and_work_save', 'handle_job_and_work_delete'),
    (Work, 'handle_job_and_work_save', 'handle_job_and_work_delete'),
  ]
  m2m = [
    Project.causes.through, Project.skills.through, Organization.causes.through
  ]

  def setup(self):
    for item in self.attach_to:
      models.signals.post_save.connect(getattr(self, item[1]), sender=item[0])
      models.signals.post_delete.connect(getattr(self, item[2]), sender=item[0])

    for item in self.m2m:
      models.signals.m2m_changed.connect(self.handle_m2m, sender=item)

  # never really called
  def teardown(self): # pragma: no cover
    for item in self.attach_to:
      models.signals.post_save.disconnect(getattr(self, item[1]), sender=item[0])
      models.signals.post_delete.disconnect(getattr(self, item[2]), sender=item[0])

    for item in self.m2m:
      models.signals.m2m_changed.disconnect(self.handle_m2m, sender=item)

  def handle_address_save(self, sender, instance, **kwargs):
    """ Custom handler for address save """
    objects = self.find_associated_with_address(instance)
    for obj in objects:
      self.handle_save(obj.__class__, obj)

  # this function is never really called on sqlite dbs
  def handle_address_delete(self, sender, instance, **kwargs):
    """ Custom handler for address delete """
    objects = self.find_associated_with_address(instance)

    # this is not called as django will delete associated project/address
    # triggering handle_delete
    for obj in objects: # pragma: no cover
      self.handle_delete(obj.__class__, obj)

  def handle_job_and_work_save(self, sender, instance, **kwargs):
    """ Custom handler for job and work save """
    self.handle_save(instance.project.__class__, instance.project)

  def handle_job_and_work_delete(self, sender, instance, **kwargs):
    """ Custom handler for job and work delete """
    self.handle_delete(instance.project.__class__, instance.project)

  def handle_m2m(self, sender, instance, **kwargs):
    """ Handle many to many relationships """
    self.handle_save(instance.__class__, instance)

  def find_associated_with_address(self, instance):
    """ Returns list with projects and organizations associated with given address """
    objects = []
    objects += list(Project.objects.filter(address=instance))
    objects += list(Organization.objects.filter(address=instance))

    return objects
