from rest_framework_csv.renderers import CSVRenderer


class ShoppingCartRenderer(CSVRenderer):
    header = ['name', 'amount', 'measurement_unit']


# import io
# import csv

# from rest_framework import renderers

# SHOPPING_CART_FILE_HEADERS = ['Ингредиент', 'Количество', 'Единица измерения']

# class ShoppingCartRenderer(renderers.BaseRenderer):
#    media_type = 'text/csv'
#    format = 'csv'

#    def render(self, data, accepted_media_type=None, renderer_context=None):
#        csv_buffer =
#        for ingredient_data in data:

#        return super().render(data, accepted_media_type, renderer_context)
