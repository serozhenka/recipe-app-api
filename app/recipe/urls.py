from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('tags', views.TagAPIViewSet, basename='tags')
router.register('ingredients', views.IngredientAPIViewSet, basename='ingredients')
router.register('recipes', views.RecipeAPIViewSet, basename='recipes')

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]