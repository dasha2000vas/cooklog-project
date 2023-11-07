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
    CreateDestroyAddViewSet, CreateDestroySubscribeViewSet, ListRetrieveViewSet
)
from .permissions import IsAuthorOrReadOnly
from .renderes import ShoppingCartRenderer
from .serializers import (
    IngredientSerializer,
    FavoriteSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    TagSerializer,
    UserSubscribeSerializer
    )
from recipes.models import (
    Ingredient, IngredientRecipe, AddedToFavorite,
    Recipe, ShoppingСart, Subscribe, Tag
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    http_method_names = ['get', 'post']

    def get_permissions(self):
        if self.action == 'me' and self.request.method == 'GET':
            return (IsAuthenticated(),)
        return super().get_permissions()

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
        if page is not None:
            serializer = UserSubscribeSerializer(
                instance=page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = UserSubscribeSerializer(
            instance=page, many=True, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        elif self.request.method == 'POST' or 'PATCH':
            return RecipePostSerializer

    def filter_queryset(self, queryset):
        if (
            self.request.user.is_anonymous
            and (
                'is_in_shopping_cart' in self.request.query_params
                or 'is_favorited' in self.request.query_params
            )
        ):
            return super().get_queryset()
        return super().filter_queryset(queryset)

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

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        renderer_classes=(ShoppingCartRenderer,)
    )
    def download_shopping_cart(self, request):
        recipes = request.user.favorite_recipes.all()
        cart = []
        for recipe in recipes:
            ingredients = recipe.ingredients.all()
            for ingredient in ingredients:
                amount = IngredientRecipe.objects.get(
                    recipe=recipe, ingredient=ingredient
                ).amount
                if (len(cart)) == 0:
                    cart.append({
                        'name': ingredient.name,
                        'amount': amount,
                        'measurement_unit': ingredient.measurement_unit
                    })
                else:
                    result = False
                    for i in range(0, len(cart)):
                        if ingredient.name == cart[i]['name']:
                            cart[i]['amount'] += amount
                            result = True
                    if not result:
                        cart.append({
                            'name': ingredient.name,
                            'amount': amount,
                            'measurement_unit': ingredient.measurement_unit
                        })
        return Response(cart)


class ShoppingCartViewSet(CreateDestroyAddViewSet):
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_object_or_404(
            ShoppingСart,
            user=self.request.user,
            recipe=Recipe.objects.get(id=self.kwargs['recipe_pk'])
        )


class FavoriteViewSet(CreateDestroyAddViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_object_or_404(
            AddedToFavorite,
            user=self.request.user,
            recipe=Recipe.objects.get(id=self.kwargs['recipe_pk'])
        )


class SubscribeViewSet(CreateDestroySubscribeViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_object_or_404(
            Subscribe,
            user=self.request.user,
            subscribed=User.objects.get(id=self.kwargs['user_pk'])
        )


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
