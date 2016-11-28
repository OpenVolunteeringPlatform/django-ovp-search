import ovp_search.apps
from django.test import TestCase
from django.core.management import call_command

class RebuildIndexTestCase(TestCase):
  def test_rebuild_index_execution(self):
    call_command('rebuild_index', '--noinput', verbosity=0)
