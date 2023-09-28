from datetime import datetime, timezone

import factory

from prev_log.models import Sale, SaleForecast, SaleForecastOpenRequest, Tendency
from prev_log.tests.factory.log import ForecastManualChangeLogFactory
from prev_log.tests.factory.utils import OriginFactory


class TendencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tendency


class SaleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Sale


class SaleForecastFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SaleForecast

    origem = factory.SubFactory(OriginFactory)


class SaleForecastOpenRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SaleForecastOpenRequest

    log = factory.SubFactory(ForecastManualChangeLogFactory)
    created_at = datetime.now(tz=timezone.utc)
