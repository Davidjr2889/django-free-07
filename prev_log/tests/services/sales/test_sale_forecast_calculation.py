from datetime import date
from typing import Any, Dict

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from prev_log.models import OrigemPrevisao, Product, SaleForecast
from prev_log.pydantic_model.product import ProductIdentification
from prev_log.services.sales.utils.forecast import (
    SALES_FORECAST_RANGE,
    update_sales_forecast,
)
from prev_log.tests.factory.product import ProductFactory
from prev_log.tests.factory.sales import SaleFactory, TendencyFactory


class SaleForecastCalculationTestCase(TestCase):
    """Sale Forecast Calculation Unit Tests"""

    filter: Dict[str, Any]
    product: Product

    def setUp(self) -> None:
        filters = {
            "familia": "familia_teste",
            "bo": "bo_teste",
            "artigo": "artigo_teste",
            "empresa": "CO",
        }
        self.filters = filters

        OrigemPrevisao.objects.create(designacao=OrigemPrevisao.AUTO)
        OrigemPrevisao.objects.create(designacao=OrigemPrevisao.MANUAL)

        self.product = ProductFactory(
            **filters,
            lead_time=35,
            min_ordr_qty=50,
            ordr_multi=2,
            stock_minimo=349,
            stock_actual=1000,
            stock_reservado=300,
            stock_encomendado=400,
        )

        TendencyFactory(
            **filters,
            base_anual=0.60,
        )

        curr_date = date.today()
        for offset in range(25):
            target_date = curr_date + relativedelta(months=offset - 24)
            qty = 500

            if offset == 24:
                qty = 0

            SaleFactory(
                **filters,
                ano=target_date.year,
                mes=target_date.month,
                qt_u=qty,
                qt_cx=qty,
                qt_cx9=qty,
            )

    def test_will_update_the_forecast_for_current_and_future_months(self):
        """"""
        # Sanity Check
        forecasts = SaleForecast.objects.all()
        self.assertEqual(len(forecasts), 0)

        # execução
        update_sales_forecast(
            filters=ProductIdentification(**self.product.__dict__),
            base_anual=0.6,
        )

        all_forecasts = SaleForecast.objects.all()
        self.assertEqual(len(all_forecasts), SALES_FORECAST_RANGE)

        curr_date = date.today()
        for offset in range(19):
            target_date = curr_date + relativedelta(months=offset)

            future_forecast = SaleForecast.objects.filter(
                **self.filters,
                ano=target_date.year,
                mes=target_date.month,
            ).first()

            self.assertGreaterEqual(future_forecast.qt_u, 800)

    def test_will_update_the_forecast_for_past_twelve_months(self):
        """"""
        # Sanity Check
        forecasts = SaleForecast.objects.all()
        self.assertEqual(len(forecasts), 0)

        # execução
        update_sales_forecast(
            filters=ProductIdentification(**self.product.__dict__),
            base_anual=0.6,
        )

        all_forecasts = SaleForecast.objects.all()
        self.assertEqual(len(all_forecasts), SALES_FORECAST_RANGE)

        curr_date = date.today()
        for offset in range(12):
            target_date = curr_date + relativedelta(months=offset - 12)

            future_forecast = SaleForecast.objects.filter(
                **self.filters,
                ano=target_date.year,
                mes=target_date.month,
            ).first()

            self.assertEqual(future_forecast.qt_u, 800)
