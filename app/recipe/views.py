from rest_framework import viewsets, mixins, permissions
from rest_framework.authentication import TokenAuthentication
from core.models import Tag
from .serializers import TagSerializer


class TagAPIViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin):
    """ Manage Tags """
    serializer_class = TagSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Tag.objects.all()

    def get_queryset(self):
        """ Return objects for current authenticated user only """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """ Create a new tag """
        serializer.save(user=self.request.user)