# Django imports.
from django.contrib.auth import get_user_model

# Third-party imports.
from rest_framework.reverse import reverse
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT)
from rest_framework.test import (APIClient, APITestCase)

# Local imports.
from ..serializers import UserSerializer

User = get_user_model()

__author__ = 'Jason Parent'


class AuthenticationTest(APITestCase):
    PASSWORD = 'pAssw0rd!'

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='user', email='user@example.com', password=self.PASSWORD)

    def test_user_can_sign_up(self):
        response = self.client.post(reverse('api:sign_up'), data={
            'username': 'new_user',
            'password1': self.PASSWORD,
            'password2': self.PASSWORD
        })
        user = User.objects.last()
        self.assertEqual(HTTP_201_CREATED, response.status_code)
        self.assertEqual(UserSerializer(user).data, response.data)

    def test_user_can_authenticate_with_valid_credentials(self):
        response = self.client.post(reverse('api:token_obtain_pair'), {
            'username': self.user.username,
            'password': 'pAssw0rd!'
        })
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_cannot_authenticate_with_invalid_credentials(self):
        response = self.client.post(reverse('api:token_obtain_pair'), {
            'username': self.user.username,
            'password': 'INVALID'
        })
        self.assertIn('non_field_errors', response.data)
