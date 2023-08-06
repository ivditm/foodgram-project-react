from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

URLS = ['tags', 'recipes',
        'users', 'ingredients']


class RecipeApiTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='test_user')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_access(self):
        for addres in URLS:
            self.assertEqual(self.client.get(f'/api/{addres}/').status_code,
                             HTTPStatus.OK)
