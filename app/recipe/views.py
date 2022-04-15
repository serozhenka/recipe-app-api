from rest_framework import viewsets, mixins, permissions
from rest_framework.authentication import TokenAuthentication
from core.models import Tag, Ingredient, Recipe
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          RecipeDetailSerializer)


class BaseRecipeAttrAPIViewSet(viewsets.GenericViewSet,
                               mixins.ListModelMixin,
                               mixins.CreateModelMixin):
    """ Manage recipe attributes [tags, ingredients] """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ Return objects for current authenticated user only """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """ Assign user to a created attribute """
        serializer.save(user=self.request.user)


class TagAPIViewSet(BaseRecipeAttrAPIViewSet):
    """ Manage Tags """
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientAPIViewSet(BaseRecipeAttrAPIViewSet):
    """ Manage Ingredients """
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

class RecipeAPIViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """ Return appropriate serializer class """
        if self.action == "retrieve":
            return RecipeDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """ Assign a user to a new recipe """
        serializer.save(user=self.request.user)