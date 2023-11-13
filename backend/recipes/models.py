from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

FIELD_RESTRICTION = 200
COLOR_FIELD_RESTRICTION = 7

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=FIELD_RESTRICTION,
        unique=True
    )
    color = models.CharField(
        'Цветовой код',
        max_length=COLOR_FIELD_RESTRICTION,
        unique=True
    )
    slug = models.SlugField(
        'Идентификатор',
        max_length=FIELD_RESTRICTION,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=FIELD_RESTRICTION)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=FIELD_RESTRICTION
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    image = models.ImageField('Картинка', upload_to='recipes/images/')
    name = models.CharField('Название', max_length=FIELD_RESTRICTION)
    text = models.TextField('Описание')
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1)]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    favorite = models.ManyToManyField(
        User,
        through='AddedToFavorite',
        related_name='favorite_recipes',
        verbose_name='Избранное'
    )
    shopping_cart = models.ManyToManyField(
        User,
        through='ShoppingСart',
        related_name='shopping_cart',
        verbose_name='Список покупок'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент')
    amount = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name_plural = 'Ингредиенты'
        unique_together = ('recipe', 'ingredient')


class AddedToFavorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )


class ShoppingСart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    subscribed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
