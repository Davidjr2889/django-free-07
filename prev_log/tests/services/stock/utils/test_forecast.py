from datetime import date, datetime, timezone
from random import randint
from typing import Any, Dict

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from prev_log.models import OrigemPrevisao, SaleForecast, StockForecast
from prev_log.pydantic_model.product import ProductIdentification
from prev_log.services.stock.utils.forecast import update_stock_forecast
from prev_log.services.utils.filters import filter_future, filter_past
from prev_log.services.utils.indexes import generate_index_from_int
from prev_log.tests.factory import (
    OpenOrderFactory,
    ProductFactory,
    SaleForecastFactory,
    StockFactory,
    StockForecastFactory,
)


def serialize_sales(filters: ProductIdentification) -> Dict[str, Any]:
    db_objects = (
        SaleForecast.objects.filter(
            **filters.dict(),
        )
        .filter(
            filter_future(),
        )
        .all()
    )

    sales = {"u": {}, "cx": {}, "cx9": {}}
    for sale_item in db_objects:
        index = generate_index_from_int(
            year=sale_item.ano,
            month=sale_item.mes,
        )

        sales["u"][index] = float(sale_item.qt_u)
        sales["cx"][index] = float(sale_item.qt_cx)
        sales["cx9"][index] = float(sale_item.qt_cx9)

    return sales


class StockForecastCalculationTestCase(TestCase):
    """Tendency Calcualtion Unit Tests"""

    filters: ProductIdentification

    def setUp(self):
        filters = {
            "familia": "familia_teste",
            "bo": "bo_teste",
            "artigo": "artigo_teste",
            "empresa": "CO",
        }
        self.filters = ProductIdentification.parse_obj(filters)

        # Setup
        ProductFactory(
            **filters,
            lead_time=35,
            min_ordr_qty=50,
            ordr_multi=2,
            stock_minimo=349,
            stock_actual=1000,
            stock_reservado=300,
            stock_encomendado=400,
        )

        # For this month's stock, let's have a few entries here
        for _ in range(10):
            StockFactory(
                dia=date.today(),
                **filters,
                armazem=str(randint(1000, 90548)),
                stock_u=100,
                stock_cx=20,
                stock_cx9=10,
            )

        # orders and sales forecast made for the rest of this month + the next 2 years
        units = 100
        sale_units = 500
        for offset in range(25):
            target_date = datetime.now(tz=timezone.utc) + relativedelta(months=offset)
            SaleForecastFactory(
                **filters,
                mes=target_date.month,
                ano=target_date.year,
                qt_u=sale_units,
                qt_cx=sale_units / 5,
                qt_cx9=sale_units / 10,
            )

            OpenOrderFactory(
                fornecedor=str(randint(1000, 90548)),
                **filters,
                previsao_data_entrega=target_date,
                mes=target_date.month,
                ano=target_date.year,
                qt_u=units,
                qt_cx=units / 5,
                qt_cx9=units / 10,
            )
            units += 20
            sale_units -= 50
            if sale_units < 0:
                sale_units = 0

        # Throw in an extra for this month's orders
        OpenOrderFactory(
            fornecedor="extra",
            **filters,
            previsao_data_entrega=datetime.now(tz=timezone.utc),
            mes=datetime.now(tz=timezone.utc).month,
            ano=datetime.now(tz=timezone.utc).year,
            qt_u=100,
            qt_cx=20,
            qt_cx9=10,
        )

        # Add a forecast of previous month that should be cleaned up
        prev_date = date.today() + relativedelta(months=-1)
        StockForecastFactory(
            **filters,
            mes=prev_date.month,
            ano=prev_date.year,
        )

    def test_can_calculate_current_month_forecast(self):
        """"""
        # Execution
        sales = serialize_sales(self.filters)
        update_stock_forecast(filters=self.filters, sales=sales)

        # Verify expectations
        curr_date = date.today()
        month = curr_date.month
        year = curr_date.year

        # For current month
        # (We are not loading fixtures, so we shouldn't have anything else in the DB for this test)
        this_month_stock = StockForecast.objects.filter(
            ano=year,
            mes=month,
        ).first()

        self.assertEqual(this_month_stock.qt_u, 600)
        self.assertEqual(this_month_stock.qt_cx, 120)
        self.assertEqual(this_month_stock.qt_cx9, 60)

    def test_can_calculate_other_months(self):
        # Execution
        sales = serialize_sales(self.filters)
        update_stock_forecast(filters=self.filters, sales=sales)

        # For the next month
        next_date = date.today() + relativedelta(months=1)
        month = next_date.month
        year = next_date.year
        forecast = StockForecast.objects.filter(
            ano=year,
            mes=month,
        ).first()

        self.assertEqual(forecast.qt_u, 270)
        self.assertEqual(forecast.qt_cx, 54)
        self.assertEqual(forecast.qt_cx9, 27)

    def test_will_set_to_zero_when_forecast_is_negative(self):
        # Execution
        sales = serialize_sales(self.filters)
        update_stock_forecast(filters=self.filters, sales=sales)

        # WHen the forecast would be a negative value
        next_date = date.today() + relativedelta(months=3)
        month = next_date.month
        year = next_date.year
        forecast = StockForecast.objects.filter(
            ano=year,
            mes=month,
        ).first()

        self.assertEqual(forecast.qt_u, 0)  # -180
        self.assertEqual(forecast.qt_cx, 0)  # -36
        self.assertEqual(forecast.qt_cx9, 0)  # - 18

    def test_will_remove_previous_months_forecast(self):
        # Execution
        sales = serialize_sales(self.filters)
        update_stock_forecast(filters=self.filters, sales=sales)

        # We should not have a forecast for the previous month...
        forecast = StockForecast.objects.filter(filter_past()).all()

        self.assertEqual(len(forecast), 0)

    def test_automatically_calculated_forecast_will_be_updated(self):
        # Add a manual  forecast for next month
        next_date = date.today() + relativedelta(months=1)

        origem = OrigemPrevisao.objects.filter(designacao=OrigemPrevisao.AUTO).first()
        if not origem:
            [origem, _] = OrigemPrevisao.objects.create(designacao=OrigemPrevisao.AUTO)

        StockForecastFactory(
            **self.filters.dict(),
            origem=origem,
            mes=next_date.month,
            ano=next_date.year,
            qt_u=1920,
            qt_cx=870,
            qt_cx9=780,
        )

        # Execution
        sales = serialize_sales(self.filters)
        update_stock_forecast(filters=self.filters, sales=sales)

        forecast = StockForecast.objects.filter(
            ano=next_date.year,
            mes=next_date.month,
        ).first()

        self.assertEqual(float(forecast.qt_u), 270)
        self.assertEqual(float(forecast.qt_cx), 54)
        self.assertEqual(float(forecast.qt_cx9), 27)

    def test_manually_inputted_forecast_will_not_be_overwritten(self):
        # Add a manual  forecast for next month
        next_date = date.today() + relativedelta(months=1)
        [origem, _] = OrigemPrevisao.objects.get_or_create(
            designacao=OrigemPrevisao.MANUAL
        )

        StockForecastFactory(
            **self.filters.dict(),
            origem=origem,
            mes=next_date.month,
            ano=next_date.year,
            qt_u=1920,
            qt_cx=870,
            qt_cx9=780,
        )

        # Execution
        sales = serialize_sales(self.filters)
        update_stock_forecast(filters=self.filters, sales=sales)

        all_forecast = StockForecast.objects.filter(
            ano=next_date.year,
            mes=next_date.month,
        ).all()

        self.assertEqual(len(all_forecast), 1)
        forecast = all_forecast[0]

        self.assertEqual(float(forecast.qt_u), 1920)
        self.assertEqual(float(forecast.qt_cx), 870)
        self.assertEqual(float(forecast.qt_cx9), 780)
