from recipes.models import IngredientRecipe
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .renderes import ShoppingCartRenderer


class DownloadShoppingCartMixin():

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        renderer_classes=(ShoppingCartRenderer,)
    )
    def download_shopping_cart(self, request):
        recipes = request.user.shopping_cart.all()
        cart = []
        for recipe in recipes:
            relations = IngredientRecipe.objects.filter(recipe=recipe)
            for relation in relations:
                ingredient = {
                    'Название': relation.ingredient.name,
                    'Количество': relation.amount,
                    'Единица измерения': relation.ingredient.measurement_unit
                }
                if (len(cart)) == 0:
                    cart.append(ingredient)
                else:
                    added = False
                    for i in range(0, len(cart)):
                        if relation.name == cart[i]['Название']:
                            cart[i]['Количество'] += relation.amount
                            added = True
                    if not added:
                        cart.append(ingredient)
        return Response(cart)
