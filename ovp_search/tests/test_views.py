from django.test import TestCase

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp_users.models import User
from ovp_projects.models import Project

class CityCountryTestCase(TestCase):
  def setUp(self):
    # Create sample projects
    user = User.objects.create_user(email="testmail@test.com", password="test_returned")
    user.save()

    project = Project(name="test project", slug="test slug", details="abc", description="abc", owner=user)
    project.save()


  def test_query_country(self):
    client = APIClient()
    response = client.get(reverse("search-list-query-country"), format="json")

    self.assertTrue(response.status_code == 200)
