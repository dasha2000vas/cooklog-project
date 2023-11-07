from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from api.views import CustomUserViewSet

v1_router = DefaultRouter()

v1_router.register('tags', views.TagViewSet)
v1_router.register(
    'recipes', views.RecipeViewSet, basename='recipes'
)
v1_router.register(
    r'recipes/(?P<recipe_pk>\d+)/shopping_cart',
    views.ShoppingCartViewSet,
    basename='shopping_cart'
)
v1_router.register(
    r'recipes/(?P<recipe_pk>\d+)/favorite',
    views.FavoriteViewSet,
    basename='favorite'
)
v1_router.register(
    r'users/(?P<user_pk>\d+)/subscribe',
    views.SubscribeViewSet,
    basename='subscribe'
)
v1_router.register('ingredients', views.IngredientViewSet)
v1_router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
