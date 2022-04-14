from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredients-list')


class PublicIngredientTestAPI(TestCase):
    """ Test publicly available ingredients API """

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """ Test login is required to access Ingredients """
        response = self.client.get(INGREDIENT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientTestAPI(TestCase):
    """ Test private Ingredients API """

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='test_password',
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients_list(self):
        """ Test retrieving a list of ingredients """
        Ingredient.objects.create(user=self.user, name='test_ingredient')
        Ingredient.objects.create(user=self.user, name='test_ingredient2')

        response = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """ Test user can only see their ingredients """
        user2 = get_user_model().objects.create_user(
            email='test2@gmail.com',
            password='test_password'
        )
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='test_ingredient'
        )
        Ingredient.objects.create(user=user2, name='test_ingredient2')

        response = self.client.get(INGREDIENT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get('name'), ingredient.name)

    def test_create_ingredients_successful(self):
        """ Test if ingredient was successfully created """
        payload = {'name': 'test_ing'}
        self.client.post(INGREDIENT_URL, payload)
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload.get('name')
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """ Test ingredient with invalid payload fails """
        payload = {'name': ''}
        response = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
