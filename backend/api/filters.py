from django.contrib.auth import get_user_model
import django_filters as filters
from django_filters.widgets import BooleanWidget

from recipes.models import Recipe

TAG_CHOICES = (
    ('breakfast', 'breakfast'), ('lunch', 'lunch'), ('dinner', 'dinner')
)

User = get_user_model()


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_favorite',
        widget=BooleanWidget
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_shopping_cart',
        widget=BooleanWidget
    )
    tags = filters.MultipleChoiceFilter(
        field_name='tags__slug',
        choices=TAG_CHOICES
    )

    class Meta:
        model = Recipe
        fields = (
            'author', 'tags'
        )

    def filter_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset
        if int(value):
            return queryset.filter(shopping_cart=user)
        return queryset.exclude(shopping_cart=user)

    def filter_favorite(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset
        if int(value):
            return queryset.filter(favorite=user)
        return queryset.exclude(favorite=user)
