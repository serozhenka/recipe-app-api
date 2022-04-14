from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
USER_URL = reverse('user:me')


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


class PublicUserAPITest(TestCase):
    """ Test user public API """

    def setUp(self) -> None:
        self.client = APIClient()
        self.payload = {
            'email': 'test@gmail.com',
            'password': 'test_password',
            'name': 'test'
        }

    def test_create_valid_user(self):
        """ Test creating user with a valid payload successful """
        response = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**response.data)
        self.assertEqual(user.email, self.payload['email'])
        self.assertEqual(user.name, self.payload['name'])
        self.assertTrue(user.check_password(self.payload['password']))
        self.assertNotIn('password', response.data)

    def test_create_user_exists(self):
        """ Test creating user that already exists """
        create_user(**self.payload)
        response = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ Test whether password is more than 5 characters """
        self.payload['password'] = 'pw'
        response = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(get_user_model().objects.filter(
            email=self.payload.get('email'),
            name=self.payload.get('name')
        ).exists())

    def test_create_token_for_user(self):
        """ Test token for the user is created """
        create_user(**self.payload)
        response = self.client.post(TOKEN_URL, self.payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_create_token_invalid_credentials(self):
        """ Test token is not created when invalid credentials provided """
        create_user(**self.payload)
        self.payload['password'] = 'wrong'

        response = self.client.post(TOKEN_URL, self.payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_without_user(self):
        """ Test token isn't created when user doesn't exist """
        response = self.client.post(TOKEN_URL, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_create_token_missing_field(self):
        """ Test that email and password fields are required """
        response = self.client.post(TOKEN_URL, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_retrieve_unauthorized_user(self):
        """ Test authentication is required for user """
        response = self.client.get(USER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITest(TestCase):
    """ Test APIs that require authentication """

    def setUp(self) -> None:
        self.user = create_user(
            email='test@gmail.com',
            password='test_password',
            name='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile(self):
        """ Test retrieving profile for authenticated user """
        response = self.client.get(USER_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'email': self.user.email,
            'name': self.user.name,
        })

    def test_post_to_user_not_allowed(self):
        """ Test post method isn't allowed on profile url """
        response = self.client.post(USER_URL, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ Test updating profile for authenticated users """
        payload = {'name': 'update', 'password': 'update'}
        response = self.client.patch(USER_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload.get('name'))
        self.assertTrue(self.user.check_password(payload.get('password')))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
