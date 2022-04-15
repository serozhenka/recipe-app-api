from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipes-list')

def detail_recipe_url(recipe_id):
    return reverse('recipe:recipes-detail', args=[recipe_id])

def sample_tag(user, name='test_tag'):
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='test_ingredient'):
    return Ingredient.objects.create(user=user, name=name)

def sample_recipe(user, **params):
    """ Create and return sample recipe """
    defaults = {
        'title': 'test',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITest(TestCase):
    """ Public recipe API Test for unauthenticated users """

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """ Test authentication is required """
        response = self.client.get(RECIPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """ Private recipe API Test for authenticated users """

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='test_password'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """ Test retrieving a list of recipes """
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        response = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_limited_to_user(self):
        """ Test retrieving recipes for current user """
        user2 = get_user_model().objects.create_user(
            email='test2@gmail.com',
            password='test_password'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        response = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_detail_recipe(self):
        """ Test recipe detail view """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        response = self.client.get(detail_recipe_url(recipe.id))
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_basic_recipe(self):
        """ Test creating recipe """
        payload = {
            'title': 'test',
            'time_minutes': 5,
            'price': 5.00,
        }
        response = self.client.post(RECIPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data.get('id'))
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """ Test creating recipe with tags """
        tag1 = sample_tag(user=self.user, name='test_tag1')
        tag2 = sample_tag(user=self.user, name='test_tag2')

        payload = {
            'title': 'test',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 5,
            'price': 5.00,
        }
        response = self.client.post(RECIPE_URL, payload)
        recipe = Recipe.objects.get(id=response.data.get('id'))
        tags = recipe.tags.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """ Test creating recipe with ingredients """
        ingredient1 = sample_ingredient(user=self.user, name='test1')
        ingredient2 = sample_ingredient(user=self.user, name='test2')

        payload = {
            'title': 'test',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 5,
            'price': 5.00,
        }
        response = self.client.post(RECIPE_URL, payload)
        recipe = Recipe.objects.get(id=response.data.get('id'))
        ingredients = recipe.ingredients.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """ Test updating a recipe """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='current')

        payload = {'title': 'test_new', 'tags': [new_tag.id]}
        url = detail_recipe_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        tags = recipe.tags.all()

        self.assertEqual(recipe.title, payload.get('title'))
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """ Test put updating for recipe """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'test_put',
            'time_minutes': 25,
            'price': 1.00,
        }
        url = detail_recipe_url(recipe.id)
        self.client.put(url, payload)
        recipe.refresh_from_db()
        tags = recipe.tags.all()

        self.assertEqual(recipe.title, payload.get('title'))
        self.assertEqual(recipe.time_minutes, payload.get('time_minutes'))
        self.assertEqual(recipe.price, payload.get('price'))
        self.assertEqual(len(tags), 0)
