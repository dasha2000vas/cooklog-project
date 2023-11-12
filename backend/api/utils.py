from django.db.models import F, Sum
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
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart=request.user
        ).annotate(
            name=F('ingredient__name')
        ).values(
            'name'
        ).annotate(
            sum=Sum('amount'),
            measurement_unit=F('ingredient__measurement_unit')
        )
        cart = []
        for ingredient in ingredients:
            cart.append({
                'Название': ingredient['name'],
                'Количество': ingredient['sum'],
                'Единица измерения': ingredient['measurement_unit']
            })
        return Response(cart)
