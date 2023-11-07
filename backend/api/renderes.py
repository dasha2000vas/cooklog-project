from rest_framework_csv.renderers import CSVRenderer


class ShoppingCartRenderer(CSVRenderer):
    header = ['name', 'amount', 'measurement_unit']
