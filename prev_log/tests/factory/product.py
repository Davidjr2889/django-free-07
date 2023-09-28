import factory

from prev_log.models import Product


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    descricao = "this is a product"
    lead_time = 60
    min_ordr_qty = 50
    # intervalos/múltiplos de quanto posso encomendar acima de min_ordr_qty
    ordr_multi = 2
