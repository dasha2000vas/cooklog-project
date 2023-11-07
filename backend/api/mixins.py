from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import RecipeAddSerializer, UserSubscribeSerializer
from recipes.models import Recipe

User = get_user_model()


class ListRetrieveViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    pass


class CreateDestroyAddViewSet(
    GenericViewSet, CreateModelMixin, DestroyModelMixin
):

    def create(self, request, *args, **kwargs):
        request.data.update({'recipe': kwargs['recipe_pk']})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        recipe = RecipeAddSerializer(
            instance=Recipe.objects.get(id=self.kwargs['recipe_pk'])
        )
        headers = self.get_success_headers(recipe.data)
        return Response(
            recipe.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        get_object_or_404(Recipe, id=self.kwargs['recipe_pk'])
        try:
            self.get_object()
        except Http404:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return self.destroy(request, *args, **kwargs)


class CreateDestroySubscribeViewSet(
    GenericViewSet, CreateModelMixin, DestroyModelMixin
):

    def create(self, request, *args, **kwargs):
        get_object_or_404(User, id=kwargs['user_pk'])
        request.data.update({'subscribed': kwargs['user_pk']})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = UserSubscribeSerializer(
            instance=User.objects.get(id=kwargs['user_pk']),
            context={'request': request}
        )
        headers = self.get_success_headers(user.data)
        return Response(
            user.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        get_object_or_404(User, id=self.kwargs['user_pk'])
        try:
            self.get_object()
        except Http404:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return self.destroy(request, *args, **kwargs)
