from datetime import date
from typing import Dict

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from prev_log.models import Product, PurchaseForecast, StockForecast
from prev_log.pydantic_model.product import ProductIdentification
from prev_log.services.purchase.utils.forecast import (
    PURCHASE_FORECAST_RANGE,
    calculate_purchase_forecast,
)
from prev_log.services.utils.filters import filter_future, filter_past
from prev_log.services.utils.indexes import generate_index_from_int
from prev_log.tests.factory import ProductFactory
from prev_log.tests.factory.sales import SaleFactory
from prev_log.tests.factory.stock import StockForecastFactory


def serialize_stock(filters: ProductIdentification):
    raw_stock = (
        StockForecast.objects.filter(
            **filters.dict(),
        )
        .filter(
            filter_future(),
        )
        .all()
    )

    stock = {"u": {}, "cx": {}, "cx9": {}}
    for stock_item in raw_stock:
        index = generate_index_from_int(
            year=stock_item.ano,
            month=stock_item.mes,
        )

        stock["u"][index] = float(stock_item.qt_u)
        stock["cx"][index] = float(stock_item.qt_cx)
        stock["cx9"][index] = float(stock_item.qt_cx9)

    return stock


class PurchaseForecastCalculationTestCase(TestCase):
    """Purchase Forecast Calculation Unit Tests"""

    product: Product
    filters: Dict[str, str]
    id_filter: ProductIdentification

    def setUp(self):
        filters = {
            "familia": "familia_teste",
            "bo": "bo_teste",
            "artigo": "artigo_teste",
            "empresa": "CO",
        }
        self.filters = filters
        self.id_filter = ProductIdentification.parse_obj(filters)

        # Setup
        self.product = ProductFactory(
            **filters,
            lead_time=0,
            min_ordr_qty=80,
            ordr_multi=10,
            stock_minimo=350,
            stock_actual=1000,
            stock_reservado=300,
            stock_encomendado=400,
        )

        curr_date = date.today()
        for offset in range(PURCHASE_FORECAST_RANGE):
            target_date = curr_date + relativedelta(months=offset)
            qty = 400

            if offset == 0:
                qty = 300
                SaleFactory(
                    **filters,
                    ano=target_date.year,
                    mes=target_date.month,
                    qt_u=200,
                    qt_cx=200,
                    qt_cx9=200,
                )

            if offset == 2:
                qty = 200

            StockForecastFactory(
                **filters,
                ano=target_date.year,
                mes=target_date.month,
                qt_u=qty,
                qt_cx=qty,
                qt_cx9=qty,
            )

    def test_will_be_zero_when_stock_forecast_over_minimum(self):
        # Sanity check
        all_stocks = StockForecast.objects.all()
        self.assertEqual(len(all_stocks), PURCHASE_FORECAST_RANGE)

        # execução
        stock = serialize_stock(self.id_filter)
        calculate_purchase_forecast(product=self.product, stock=stock)

        # With 0 lead time, we should have forecasts for all months to go + current
        all_forecasts = PurchaseForecast.objects.all()
        self.assertEqual(len(all_forecasts), PURCHASE_FORECAST_RANGE)

        # Setup makes almost all stocks higher than minimum. Then let's pick next month
        # (this month's calculation is a bit special, so let's do it another time)
        target_date = date.today() + relativedelta(months=1)
        future_forecast = PurchaseForecast.objects.filter(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
        ).first()
        if not future_forecast:
            raise Exception("Houston, we have a problem")

        self.assertEqual(future_forecast.qt_u, 0)

    def test_will_honor_min_qty(self):
        """"""
        # We cant to do one thing at a time here
        self.product.min_ordr_qty = 170
        self.product.ordr_multi = 1
        self.product.save()

        # execução
        stock = serialize_stock(self.id_filter)
        calculate_purchase_forecast(product=self.product, stock=stock)

        # With 0 lead time, we should have forecasts for all months to go + current
        all_forecasts = PurchaseForecast.objects.all()
        self.assertEqual(len(all_forecasts), PURCHASE_FORECAST_RANGE)

        # two months from now, stock forecast is less than minimum.
        target_date = date.today() + relativedelta(months=2)
        future_forecast = PurchaseForecast.objects.filter(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
        ).first()
        if not future_forecast:
            raise Exception("Houston, we have a problem")

        self.assertEqual(future_forecast.qt_u, 170)

    def test_will_honor_ord_mult(self):
        # We cant to do one thing at a time here
        self.product.min_ordr_qty = 1
        self.product.ordr_multi = 11
        self.product.save()

        # execução
        stock = serialize_stock(self.id_filter)
        calculate_purchase_forecast(product=self.product, stock=stock)

        # With 0 lead time, we should have forecasts for all months to go + current
        all_forecasts = PurchaseForecast.objects.all()
        self.assertEqual(len(all_forecasts), PURCHASE_FORECAST_RANGE)

        # two months from now, stock forecast is less than minimum.
        target_date = date.today() + relativedelta(months=2)
        future_forecast = PurchaseForecast.objects.filter(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
        ).first()
        if not future_forecast:
            raise Exception("Houston, we have a problem")

        self.assertEqual(future_forecast.qt_u, 154)

    def test_will_both_ord_multi_and_min_qty(self):
        # Now we want check both in conjunction
        self.product.min_ordr_qty = 400
        self.product.ordr_multi = 11
        self.product.save()

        # execução
        stock = serialize_stock(self.id_filter)
        calculate_purchase_forecast(product=self.product, stock=stock)

        # With 0 lead time, we should have forecasts for all months to go + current
        all_forecasts = PurchaseForecast.objects.all()
        self.assertEqual(len(all_forecasts), PURCHASE_FORECAST_RANGE)

        # two months from now, stock forecast is less than minimum.
        target_date = date.today() + relativedelta(months=2)
        future_forecast = PurchaseForecast.objects.filter(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
        ).first()
        if not future_forecast:
            raise Exception("Houston, we have a problem")

        self.assertEqual(future_forecast.qt_u, 407)

    def test_will_apply_the_lead_time_to_the_forecast(self):
        # Apply some lead time of 55 days
        lead_time = 55
        self.product.lead_time = lead_time
        self.product.save()

        # execução
        stock = serialize_stock(self.id_filter)
        calculate_purchase_forecast(product=self.product, stock=stock)

        # two months from now, stock forecast is less than minimum. BUT, there is the lead time now!
        target_date = date.today() + relativedelta(
            months=2,
            days=-lead_time,
        )

        future_forecast = PurchaseForecast.objects.filter(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
        ).first()
        if not future_forecast:
            raise Exception("Houston, we have a problem")

        self.assertEqual(future_forecast.qt_u, 150)
        self.assertEqual(future_forecast.data_limite_pedido.date(), target_date)

    def test_will_clean_previous_months_forecast_but_keep_others(self):
        # Apply some lead time of 55 days, so we should have
        # one forecast in the past and one forecast for this month
        lead_time = 55
        self.product.lead_time = lead_time
        self.product.save()

        # execução
        stock = serialize_stock(self.id_filter)
        calculate_purchase_forecast(product=self.product, stock=stock)

        # two months from now, stock forecast is less than minimum. BUT, there is the lead time now!
        curr_date = date.today()

        past_forecast = (
            PurchaseForecast.objects.filter(**self.filters).filter(filter_past()).all()
        )
        self.assertEqual(len(past_forecast), 0)

        # We should still have this month though
        curr_date = date.today()
        curr_month_forecast = PurchaseForecast.objects.filter(
            **self.filters,
            ano=curr_date.year,
            mes=curr_date.month,
        ).all()
        self.assertEqual(len(curr_month_forecast), 1)
