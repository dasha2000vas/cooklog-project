import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import (
    UserCreateSerializer, UserSerializer
)
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Ingredient, IngredientRecipe, AddedToFavorite,
    Recipe, ShoppingСart, Subscribe, Tag
)

User = get_user_model()


class UserPostSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


class UserGetSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscribe.objects.filter(
            user=user.id, subscribed=obj.id
        ).exists()


class RecipeAddSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscribe.objects.filter(
            user=user.id, subscribed=obj.id
        ).exists()

    def get_recipes(self, obj):
        try:
            i = int(self.context['request'].query_params['recipes_limit'])
            recipes = obj.recipes.all()[:i]
        except KeyError:
            recipes = obj.recipes.all()
        return RecipeAddSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return len(obj.recipes.all())


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientPostSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(required=True)

    def validate_id(self, value):
        if not value:
            raise ValidationError('Пожалуйста, добавьте ингредиент')
        try:
            Ingredient.objects.get(id=value)
        except Ingredient.DoesNotExist:
            raise ValidationError('Такого ингредиента нет в списке')
        return value

    def validate_amount(self, value):
        if not value:
            raise ValidationError('Пожалуйста, укажите количество ингредиента')
        return value


class IngredientGetSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField(default=1)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)

    def get_amount(self, obj):
        recipe = self.context['recipe']
        return get_object_or_404(
            IngredientRecipe,
            recipe=recipe, ingredient=obj
        ).amount


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            filetype = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name='temp.' + filetype
            )
        return super().to_internal_value(data)


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        required=True,
        many=True
    )
    image = Base64ImageField(required=True, allow_null=False)
    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    ingredients = IngredientPostSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
            'pub_date',
        )

    def validate(self, attrs):
        try:
            attrs['ingredients']
        except KeyError:
            raise ValidationError()
        try:
            attrs['tags']
        except KeyError:
            raise ValidationError()
        return super().validate(attrs)

    def validate_ingredients(self, lst):
        if len(lst) == 0:
            raise ValidationError(
                'Пожалуйста, укажите хотя бы один ингредиент'
            )
        temp = []
        for ingr in lst:
            if ingr['id'] not in temp:
                temp.append(ingr['id'])
            else:
                raise ValidationError('Ингредиенты не должны повторятся')
        return lst

    def validate_tags(self, lst):
        if len(lst) == 0:
            raise ValidationError('Пожалуйста, укажите хотя бы один тег')
        if len(lst) == len(set(lst)):
            return lst
        raise ValidationError('Теги не должны повторятся')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_in_recipe in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_in_recipe['id']
            )
            amount = ingredient_in_recipe['amount']
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        for ingredient_in_recipe in ingredients:
            print(ingredient_in_recipe)
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_in_recipe['id']
            )
            amount = ingredient_in_recipe['amount']
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=amount
            )
        instance.save()
        return instance


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserGetSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        context = getattr(self, 'context', None) or {}
        context['recipe'] = obj
        return IngredientGetSerializer(
            obj.ingredients.all(), many=True, context=context
        ).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return AddedToFavorite.objects.filter(user=user.id, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return ShoppingСart.objects.filter(
            user=user.id, recipe=obj
        ).exists()


class SubscribeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    subscribed = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        fields = ('id', 'user', 'subscribed')
        model = Subscribe

        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'subscribed')
            )
        ]

    def validate_subscribed(self, obj):
        if obj == self.context['request'].user:
            raise serializers.ValidationError()
        return obj


class FavoriteSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        read_only=True, default=serializers.CurrentUserDefault(),
        slug_field='username'
    )
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        fields = ('id', 'user', 'recipe')
        model = AddedToFavorite

        validators = [
            UniqueTogetherValidator(
                queryset=AddedToFavorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        slug_field='username'
    )
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        fields = ('id', 'user', 'recipe')
        model = ShoppingСart

        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingСart.objects.all(),
                fields=('user', 'recipe')
            )
        ]
