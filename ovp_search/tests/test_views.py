from django.test import TestCase
from django.core.management import call_command

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp_users.models import User
from ovp_projects.models import Project
from ovp_core.models import GoogleAddress


class CityCountryTestCase(TestCase):
  def setUp(self):
    call_command('clear_index', '--noinput', verbosity=0)

    # Create sample projects
    user = User.objects.create_user(email="testmail@test.com", password="test_returned")
    user.save()

    address1 = GoogleAddress(typed_address="São paulo, SP - Brazil")
    address2 = GoogleAddress(typed_address="Campinas, SP - Brazil")
    address3 = GoogleAddress(typed_address="New york - United States")
    address1.save()
    address2.save()
    address3.save()

    project = Project(name="test project", slug="test-slug", details="abc", description="abc", owner=user, address=address1, published=True)
    project.save()

    project = Project(name="test project2", slug="test-slug2", details="abc", description="abc", owner=user, address=address2, published=True)
    project.save()

    project = Project(name="test project3", slug="test-slug2", details="abc", description="abc", owner=user, address=address3, published=True)
    project.save()



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


