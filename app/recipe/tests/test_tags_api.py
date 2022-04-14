from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tags-list')


class PublicTagsAPITest(TestCase):
    """ Test publicly available tags API """

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """ Test login is required for retrieving tags """
        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITest(TestCase):
    """ Test authorized user tags API """
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='test_password'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """ Test retrieving tags """
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='dessert')

        response = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ Test tags returned are authenticated user's tags """
        user2 = get_user_model().objects.create_user(
            email='test2@gmail.com',
            password='test_password2'
        )
        Tag.objects.create(user=user2, name='fruity')
        tag = Tag.objects.create(user=self.user, name='chocolate')

        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_create_tags_successfully(self):
        """ Test creating a new tag"""
        payload = {'name': 'test'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload.get('name')
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid_name(self):
        """ Test creating new tag with invalid payload """
        payload = {'name': ''}
        response = self.client.post(TAGS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
