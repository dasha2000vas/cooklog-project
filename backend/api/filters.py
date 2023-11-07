from django.contrib.auth import get_user_model
import django_filters as filters

from recipes.models import Recipe

BOOLEAN_CHOICES = ((0, 0), (1, 1))
TAG_CHOICES = (
    ('breakfast', 'breakfast'), ('lunch', 'lunch'), ('dinner', 'dinner')
)

User = get_user_model()


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.ChoiceFilter(
        field_name='is_favorited',
        choices=BOOLEAN_CHOICES,
        method='filter_favorite'
    )
    is_in_shopping_cart = filters.ChoiceFilter(
        field_name='is_in_shopping_cart',
        choices=BOOLEAN_CHOICES,
        method='filter_shopping_cart'
    )
    author = filters.ModelChoiceFilter(
        field_name='author',
        queryset=User.objects.all(),
        to_field_name='id'
        )
    tags = filters.MultipleChoiceFilter(
        field_name='tags__slug',
        choices=TAG_CHOICES
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited', 'is_in_shopping_cart', 'author', 'tags'
        )

    def filter_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if int(value):
            return Recipe.objects.filter(shopping_cart=user)
        elif not int(value):
            return Recipe.objects.exclude(shopping_cart=user)

    def filter_favorite(self, queryset, name, value):
        user = self.request.user
        if int(value):
            return Recipe.objects.filter(favorite=user)
        elif not int(value):
            return Recipe.objects.exclude(favorite=user)
