from rest_framework import viewsets, mixins, permissions
from rest_framework.authentication import TokenAuthentication
from core.models import Tag, Ingredient
from .serializers import TagSerializer, IngredientSerializer


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
