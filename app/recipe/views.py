from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.authentication import TokenAuthentication
from core.models import Tag, Ingredient, Recipe
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          RecipeDetailSerializer,
                          RecipeImageSerializer)


class BaseRecipeAttrAPIViewSet(viewsets.GenericViewSet,
                               mixins.ListModelMixin,
                               mixins.CreateModelMixin):
    """ Manage recipe attributes [tags, ingredients] """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ Return objects for current authenticated user only """
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False).distinct()
        return queryset.filter(user=self.request.user).order_by('-name')

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

    def _params_to_int(self, qs):
        """ Convert list of string IDs to integers """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_int(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingredients_ids = self._params_to_int(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_ids)

        return queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """ Return appropriate serializer class """
        if self.action == "retrieve":
            return RecipeDetailSerializer
        elif self.action == "upload_image":
            return RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """ Assign a user to a new recipe """
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """ Upload an image to a recipe """
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

