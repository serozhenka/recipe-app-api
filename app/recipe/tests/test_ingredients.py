from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Recipe
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

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """ Test filtering ingredients to those assigned to recipes """
        ingredient1 = Ingredient.objects.create(
            user=self.user, name='ingredient1'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user, name='ingredient2'
        )

        recipe = Recipe.objects.create(
            title='recipe',
            user=self.user,
            time_minutes=5,
            price=5.00
        )
        recipe.ingredients.add(ingredient1)

        response = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_retrieve_ingredients_assigned_unique(self):
        ingredient = Ingredient.objects.create(
            user=self.user, name='ingredient1'
        )
        Ingredient.objects.create(
            user=self.user, name='ingredient2'
        )

        recipe1 = Recipe.objects.create(
            title='recipe1',
            user=self.user,
            time_minutes=5,
            price=5.00
        )
        recipe2 = Recipe.objects.create(
            title='recipe2',
            user=self.user,
            time_minutes=10,
            price=10.00
        )
        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        response = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        serializer = IngredientSerializer(ingredient)

        self.assertEqual(len(response.data), 1)
        self.assertIn(serializer.data, response.data)

