from rest_framework_csv.renderers import CSVRenderer


class ShoppingCartRenderer(CSVRenderer):
    header = ['Название', 'Количество', 'Единица измерения']
