from datetime import datetime, timezone

import factory

from prev_log.models import OpenOrder, PurchaseForecast, PurchaseForecastOpenRequest
from prev_log.tests.factory.log import ForecastManualChangeLogFactory
from prev_log.tests.factory.utils import OriginFactory


class OpenOrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OpenOrder


class PurchaseForecastFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PurchaseForecast

    origem = factory.SubFactory(OriginFactory)
    data_limite_pedido = datetime.now(tz=timezone.utc)


class PurchaseForecastOpenRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PurchaseForecastOpenRequest

    log = factory.SubFactory(ForecastManualChangeLogFactory)
    created_at = datetime.now(tz=timezone.utc)
