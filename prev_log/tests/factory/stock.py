from datetime import datetime, timezone

import factory

from prev_log.models import Stock, StockForecast, StockForecastOpenRequest
from prev_log.tests.factory.log import ForecastManualChangeLogFactory
from prev_log.tests.factory.utils import OriginFactory


class StockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Stock


class StockForecastFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StockForecast

    origem = factory.SubFactory(OriginFactory)


class StockForecastOpenRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StockForecastOpenRequest

    log = factory.SubFactory(ForecastManualChangeLogFactory)
    created_at = datetime.now(tz=timezone.utc)
