from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import RecipeFilter
from .mixins import (
    CreateDestroyRelationshipViewSet, ListRetrieveViewSet
)
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    FavoriteSerializer,
    RecipeAddSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    TagSerializer,
    UserSubscribeSerializer
)
from .utils import DownloadShoppingCartMixin
from recipes.models import (
    Ingredient,
    AddedToFavorite,
    Recipe,
    ShoppingСart,
    Subscribe,
    Tag
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    http_method_names = ['get', 'post']

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        sub_id = request.user.subscriptions.all().values_list(
            'subscribed', flat=True
        )
        subscriptions = User.objects.filter(id__in=sub_id)
        page = self.paginate_queryset(subscriptions)
        serializer = UserSubscribeSerializer(
            instance=page, many=True, context={'request': request}
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(ModelViewSet, DownloadShoppingCartMixin):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        elif self.request.method in ['POST', 'PATCH']:
            return RecipePostSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(author=request.user)
        recipe = RecipeGetSerializer(
            instance=instance, context={'request': request}
        )
        headers = self.get_success_headers(recipe.data)
        return Response(
            recipe.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        rcp_instance = serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        recipe = RecipeGetSerializer(
            instance=rcp_instance, context={'request': request}
        )
        return Response(
            recipe.data, status=status.HTTP_200_OK
        )


class ShoppingCartViewSet(CreateDestroyRelationshipViewSet):
    serializer_class = ShoppingCartSerializer

    def get_object(self):
        return get_object_or_404(
            ShoppingСart,
            user=self.request.user,
            recipe=Recipe.objects.get(id=self.kwargs['recipe_pk'])
        )

    def create(
        self, request, *args, **kwargs
    ):
        return super().create(
            request,
            field='recipe',
            key='recipe_pk',
            post_serializer=RecipeAddSerializer,
            model=Recipe,
            *args,
            **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().delete(
            request, model=Recipe, key='recipe_pk', *args, **kwargs
        )


class FavoriteViewSet(CreateDestroyRelationshipViewSet):
    serializer_class = FavoriteSerializer

    def get_object(self):
        return get_object_or_404(
            AddedToFavorite,
            user=self.request.user,
            recipe=Recipe.objects.get(id=self.kwargs['recipe_pk'])
        )

    def create(
        self, request, *args, **kwargs
    ):
        return super().create(
            request,
            field='recipe',
            key='recipe_pk',
            post_serializer=RecipeAddSerializer,
            model=Recipe,
            *args,
            **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().delete(
            request, model=Recipe, key='recipe_pk', *args, **kwargs
        )


class SubscribeViewSet(CreateDestroyRelationshipViewSet):
    serializer_class = SubscribeSerializer

    def get_object(self):
        return get_object_or_404(
            Subscribe,
            user=self.request.user,
            subscribed=User.objects.get(id=self.kwargs['user_pk'])
        )

    def create(
        self, request, *args, **kwargs
    ):
        get_object_or_404(User, id=self.kwargs['user_pk'])
        return super().create(
            request,
            field='subscribed',
            key='user_pk',
            post_serializer=UserSubscribeSerializer,
            model=User,
            *args,
            **kwargs
        )

    def delete(self, request, *args, **kwargs):
        return super().delete(
            request, model=User, key='user_pk', *args, **kwargs
        )


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
