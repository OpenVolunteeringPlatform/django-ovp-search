from django.test import TestCase
from django.test.utils import override_settings
from django.core.management import call_command
from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp_users.models import User
from ovp_projects.models import Project, Job
from ovp_organizations.models import Organization
from ovp_core.models import GoogleAddress, Cause, Skill

import json



"""
Helpers
"""
def create_sample_projects():
  # Create sample projects
  user = User.objects.create_user(email="testmail@test.com", password="test_returned")
  user.save()

  address1 = GoogleAddress(typed_address="São paulo, SP - Brazil")
  address2 = GoogleAddress(typed_address="Campinas, SP - Brazil")
  address3 = GoogleAddress(typed_address="New york - United States")
  address4 = GoogleAddress(typed_address="New york - United States")
  address1.save()
  address2.save()
  address3.save()
  address4.save()

  # TODO: Implement when Organization has slug
  #organization = Organization(name="test filter by org", slug="filter-by-org", details="abc", owner=user, address=address1, published=True, type=0)
  #organization.save()

  project = Project(name="test project", slug="test-slug", details="abc", description="abc", owner=user, address=address1, published=True)
  project.save()
  project.causes.add(Cause.objects.all().order_by('pk')[0])
  project.skills.add(Skill.objects.all().order_by('pk')[0])

  project = Project(name="test project2", slug="test-slug2", details="abc", description="abc", owner=user, address=address2, highlighted=True, published=True)
  project.save()
  project.causes.add(Cause.objects.all().order_by('pk')[1])

  project = Project(name="test project3", slug="test-slug3", details="abc", description="abc", owner=user, address=address3, published=True)
  project.save()
  project.skills.add(Skill.objects.all().order_by('pk')[1])
  job = Job(can_be_done_remotely=True, project=project)
  job.save()

  project = Project(name="test project4", slug="test-slug4", details="abc", description="abc", owner=user, address=address4, published=False)
  project.save()

def create_sample_organizations():
  user = User.objects.create_user(email="testmail@test.com", password="test_returned")
  user.save()

  address1 = GoogleAddress(typed_address="São paulo, SP - Brazil")
  address2 = GoogleAddress(typed_address="Campinas, SP - Brazil")
  address3 = GoogleAddress(typed_address="New york - United States")
  address4 = GoogleAddress(typed_address="New york - United States")
  address1.save()
  address2.save()
  address3.save()
  address4.save()

  organization = Organization(name="test organization", details="abc", owner=user, address=address1, published=True, type=0)
  organization.save()
  organization.causes.add(Cause.objects.all().order_by('pk')[0])

  organization = Organization(name="test organization2", details="abc", owner=user, address=address2, published=True, highlighted=True, type=0)
  organization.save()
  organization.causes.add(Cause.objects.all().order_by('pk')[1])

  organization = Organization(name="test organization3", details="abc", owner=user, address=address3, published=True, type=0)
  organization.save()

  organization = Organization(name="test organization4", details="abc", owner=user, address=address4, published=False, type=0)
  organization.save()


"""
Tests
"""
class ProjectSearchTestCase(TestCase):
  def setUp(self):
    call_command('clear_index', '--noinput', verbosity=0)
    create_sample_projects()
    self.client = APIClient()

  def test_query_optimization(self):
    """
    Test project search does only 3 queries
    """
    cache.clear()
    with self.assertNumQueries(3):
      response = self.client.get(reverse("search-projects-list"), format="json")

  def test_query_gets_cached(self):
    """
    Test project search gets cached
    """
    cache.clear()
    response = self.client.get(reverse("search-projects-list"), format="json")

    # Second request should not hit db
    with self.assertNumQueries(0):
      response = self.client.get(reverse("search-projects-list"), format="json")

  def test_no_filter(self):
    """
    Test searching with no filters return all available projects
    """
    response = self.client.get(reverse("search-projects-list"), format="json")
    self.assertTrue(len(response.data["results"]) == 3)


  def test_publish_filter(self):
    """
    Test searching with publish filter == "true", "false" and "both" return correct projects
    """
    response = self.client.get(reverse("search-projects-list") + "?published=true", format="json")
    self.assertTrue(len(response.data["results"]) == 3)

    response = self.client.get(reverse("search-projects-list") + "?published=false", format="json")
    self.assertTrue(len(response.data["results"]) == 1)

    response = self.client.get(reverse("search-projects-list") + "?published=both", format="json")
    self.assertTrue(len(response.data["results"]) == 4)

  # TODO: Implement when Organization has slug
  #def test_organization_filter(self):
  #  """
  #  Test searching with organization filter returns only projects from organization
  #  """
  #  response = self.client.get(reverse("search-projects-list") + "?organization=filter-by-org", format="json")
  #  self.assertTrue(len(response.data["results"]) == 1)

  def test_name_filter(self):
    """
    Test searching with name filter returns project filtered by name(ngram)
    """
    response = self.client.get(reverse("search-projects-list") + "?name=roject2", format="json")
    self.assertTrue(len(response.data["results"]) == 1)

  def test_highlighted_filter(self):
    """
    Test searching with highlighted=true returns only highlighted fields
    """
    response = self.client.get(reverse("search-projects-list") + "?highlighted=true", format="json")
    self.assertTrue(len(response.data["results"]) == 1)
    self.assertTrue(response.data["results"][0]["name"] == "test project2")

  def test_address_filter(self):
    """
    Test searching with address filter returns only results filtered by address
    """
    # Filter by city
    response = self.client.get(reverse("search-projects-list") + '?address={"address_components":[{"types":["locality"], "long_name":"São Paulo"}]}', format="json")
    self.assertTrue(len(response.data["results"]) == 1)

    # Filter by state
    response = self.client.get(reverse("search-projects-list") + '?address={"address_components":[{"types":["administrative_area_level_1"], "long_name":"State of São Paulo"}]}', format="json")
    self.assertTrue(len(response.data["results"]) == 2)

    # Filter by country
    response = self.client.get(reverse("search-projects-list") + '?address={"address_components":[{"types":["country"], "long_name":"United States"}]}', format="json")
    self.assertTrue(len(response.data["results"]) == 1)

    # Filter remote jobs
    response = self.client.get(reverse("search-projects-list") + '?address={"address_components":[]}', format="json")
    self.assertTrue(len(response.data["results"]) == 1)


  def test_causes_filter(self):
    """
    Test searching with causes filter returns only results filtered by cause
    """
    cause_id1 = Cause.objects.all().order_by('pk')[0].pk
    cause_id2 = Cause.objects.all().order_by('pk')[1].pk

    response = self.client.get(reverse("search-projects-list") + "?cause=" + str(cause_id1), format="json")
    self.assertTrue(len(response.data["results"]) == 1)
    self.assertTrue(response.data["results"][0]["name"] == "test project")

    response = self.client.get(reverse("search-projects-list") + "?cause=" + str(cause_id2), format="json")
    self.assertTrue(len(response.data["results"]) == 1)
    self.assertTrue(response.data["results"][0]["name"] == "test project2")

    response = self.client.get(reverse("search-projects-list") + "?cause={},{}".format(cause_id1, cause_id2), format="json")
    self.assertTrue(len(response.data["results"]) == 2)


  def test_skills_filter(self):
    """
    Test searching with skill filter returns only results filtered by skill
    """
    skill_id1 = Skill.objects.all().order_by('pk')[0].pk
    skill_id2 = Skill.objects.all().order_by('pk')[1].pk

    response = self.client.get(reverse("search-projects-list") + "?skill=" + str(skill_id1), format="json")
    self.assertTrue(len(response.data["results"]) == 1)
    self.assertTrue(response.data["results"][0]["name"] == "test project")

    response = self.client.get(reverse("search-projects-list") + "?skill=" + str(skill_id2), format="json")
    self.assertTrue(len(response.data["results"]) == 1)
    self.assertTrue(response.data["results"][0]["name"] == "test project3")

    response = self.client.get(reverse("search-projects-list") + "?skill={},{}".format(skill_id1, skill_id2), format="json")
    self.assertTrue(len(response.data["results"]) == 2)


  def test_query_filter(self):
    """
    Test searching with query filter returns only results filtered by text query
    """
    response = self.client.get(reverse("search-projects-list") + "?query=project3", format="json")
    self.assertTrue(len(response.data["results"]) == 1)
    self.assertTrue(response.data["results"][0]["name"] == "test project3")

    response = self.client.get(reverse("search-projects-list") + "?query=project4", format="json")
    self.assertTrue(len(response.data["results"]) == 0)


class OrganizationSearchTestCase(TestCase):
  def setUp(self):
    call_command('clear_index', '--noinput', verbosity=0)
    create_sample_organizations()
    self.client = APIClient()

  def test_query_optimization(self):
    """
    Test organization search does only 2 queries
    """
    cache.clear()
    with self.assertNumQueries(2):
      response = self.client.get(reverse("search-organizations-list"), format="json")

  def test_query_gets_cached(self):
    """
    Test organization search gets cached
    """
    cache.clear()
    response = self.client.get(reverse("search-organizations-list"), format="json")

    # Second request should not hit db
    with self.assertNumQueries(0):
      response = self.client.get(reverse("search-organizations-list"), format="json")

  def test_no_filter(self):
    """
    Test searching with no filters return all available projects
    """
    response = self.client.get(reverse("search-organizations-list"), format="json")
    self.assertTrue(len(response.data["results"]) == 3)

  def test_publish_filter(self):
    """
    Test searching with publish filter == "true", "false" and "both" return correct organizations
    """
    response = self.client.get(reverse("search-organizations-list") + "?published=true", format="json")
    self.assertTrue(len(response.data["results"]) == 3)

    response = self.client.get(reverse("search-organizations-list") + "?published=false", format="json")
    self.assertTrue(len(response.data["results"]) == 1)

    response = self.client.get(reverse("search-organizations-list") + "?published=both", format="json")
    self.assertTrue(len(response.data["results"]) == 4)

  def test_name_filter(self):
    """
    Test searching with name filter returns organizations filtered by name(ngram)
    """
    response = self.client.get(reverse("search-organizations-list") + "?name=rganization2", format="json")
    self.assertTrue(len(response.data["results"]) == 1)

  def test_highlighted_filter(self):
    """
    Test searching with highlighted=true returns only highlighted fields
    """
    response = self.client.get(reverse("search-organizations-list") + "?highlighted=true", format="json")
    self.assertTrue(len(response.data["results"]) == 1)
    self.assertTrue(response.data["results"][0]["name"] == "test organization2")

  def test_address_filter(self):
    """
    Test searching with address filter returns only results filtered by address
    """
    # Filter by city
    response = self.client.get(reverse("search-organizations-list") + '?address={"address_components":[{"types":["locality"], "long_name":"São Paulo"}]}', format="json")
    self.assertTrue(len(response.data["results"]) == 1)

    # Filter by state
    response = self.client.get(reverse("search-organizations-list") + '?address={"address_components":[{"types":["administrative_area_level_1"], "long_name":"State of São Paulo"}]}', format="json")
    self.assertTrue(len(response.data["results"]) == 2)

    # Filter by country
    response = self.client.get(reverse("search-organizations-list") + '?address={"address_components":[{"types":["country"], "long_name":"United States"}]}', format="json")
    self.assertTrue(len(response.data["results"]) == 1)


  def test_causes_filter(self):
    """
    Test searching with causes filter returns only results filtered by cause
    """
    cause_id1 = Cause.objects.all().order_by('pk')[0].pk
    cause_id2 = Cause.objects.all().order_by('pk')[1].pk

    response = self.client.get(reverse("search-organizations-list") + "?cause=" + str(cause_id1), format="json")
    self.assertTrue(len(response.data["results"]) == 1)
    self.assertTrue(response.data["results"][0]["name"] == "test organization")

    response = self.client.get(reverse("search-organizations-list") + "?cause=" + str(cause_id2), format="json")
    self.assertTrue(len(response.data["results"]) == 1)
    self.assertTrue(response.data["results"][0]["name"] == "test organization2")

    response = self.client.get(reverse("search-organizations-list") + "?cause={},{}".format(cause_id1, cause_id2), format="json")
    self.assertTrue(len(response.data["results"]) == 2)


  def test_query_filter(self):
    """
    Test searching with query filter returns only results filtered by text query
    """
    response = self.client.get(reverse("search-organizations-list") + "?query=organization3", format="json")
    self.assertTrue(len(response.data["results"]) == 1)
    self.assertTrue(response.data["results"][0]["name"] == "test organization3")

    response = self.client.get(reverse("search-organizations-list") + "?query=organization4", format="json")
    self.assertTrue(len(response.data["results"]) == 0)


@override_settings(OVP_CORE={'MAPS_API_LANGUAGE': 'en_US'})
class CityCountryTestCase(TestCase):
  def setUp(self):
    call_command('clear_index', '--noinput', verbosity=0)
    create_sample_projects()


  def test_query_country(self):
    client = APIClient()

    response = client.get(reverse("search-query-country", ["Brazil"]), format="json")
    self.assertTrue(response.status_code == 200)
    self.assertTrue(len(response.data) == 2)
    self.assertTrue("Campinas" in response.data)
    self.assertTrue("São Paulo" in response.data)

    response = client.get(reverse("search-query-country", ["United States"]), format="json")
    self.assertTrue(response.status_code == 200)
    self.assertTrue(len(response.data) == 1)
    self.assertTrue("New York" in response.data)
