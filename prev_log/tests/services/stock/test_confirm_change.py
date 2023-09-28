from datetime import datetime, timezone
from random import randint
from typing import Dict, cast

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from prev_log.exceptions import PrevLogBadRequestException
from prev_log.models import (
    ForecastManualChangeLog,
    OrigemPrevisao,
    Product,
    StockForecast,
    StockForecastOpenRequest,
)
from prev_log.pydantic_model.stock import ConfirmRequestParams
from prev_log.services.stock.change import confirm_stock_change_request
from prev_log.services.utils.log import ManualChangeStatus
from prev_log.tests.factory import ProductFactory, StockForecastFactory
from prev_log.tests.factory.stock import StockForecastOpenRequestFactory


class StockForecastConfirmChangeTestCase(TestCase):
    """Tendency Calcualtion Unit Tests"""

    product: Product
    filters: Dict[str, str]

    def setUp(self):
        filters = {
            "familia": "familia_teste",
            "bo": "bo_teste",
            "artigo": "artigo_teste",
            "empresa": "CO",
        }
        self.filters = filters

        # Setup
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

        OrigemPrevisao.objects.create(designacao=OrigemPrevisao.AUTO)
        OrigemPrevisao.objects.create(designacao=OrigemPrevisao.MANUAL)

    def stub_forecast_request(
        self, target_date: datetime, new_qty: int, curr_qty: int = 500
    ):
        # current forecast
        StockForecastFactory(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
            qt_u=curr_qty,
            qt_cx=curr_qty,
            qt_cx9=curr_qty,
        )

        # New request
        request = StockForecastOpenRequestFactory(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
            utilizador_id=randint(100, 500),
            qt_u=new_qty,
            qt_cx=new_qty / 5,
            qt_cx9=new_qty / 10,
        )

        return request

    def test_confirming_change_to_invalid_request_will_raise(self):
        """"""
        # Execution
        params = ConfirmRequestParams(
            **self.filters,
            status=ManualChangeStatus.APPROVED.value,
            request_id=-50,
            utilizador_id=678,
            utilizador="employee of the month",
            comentario="a random comment to request this",
        )

        with self.assertRaises(PrevLogBadRequestException) as context:
            confirm_stock_change_request(params=params)

        exc = context.exception
        self.assertEqual(exc.status, 400)
        self.assertEqual(exc.error, "stock confirm request")
        self.assertEqual(exc.details, "invalid request")

    def test_confirming_change_will_change_the_forecast(self):
        """"""
        # setup
        user_id = 678
        new_qty = 1300
        target_date = datetime.now(tz=timezone.utc) + relativedelta(months=5)
        request = self.stub_forecast_request(target_date=target_date, new_qty=new_qty)

        # Execution
        params = ConfirmRequestParams(
            **self.filters,
            status=ManualChangeStatus.APPROVED.value,
            request_id=request.id,
            utilizador_id=user_id,
            utilizador="employee of the month",
            comentario="a random comment to request this",
        )
        confirm_stock_change_request(params=params)

        # Verify
        # (We are not loading fixtures, so we shouldn't have anything else in the DB for this test)
        forecasted = StockForecast.objects.filter(
            ano=target_date.year,
            mes=target_date.month,
        ).first()

        self.assertEqual(float(forecasted.qt_u), new_qty)
        self.assertEqual(float(forecasted.qt_cx), new_qty / 5)
        self.assertEqual(float(forecasted.qt_cx9), new_qty / 10)

        # We still need to have a log with the decision though
        all_logs = ForecastManualChangeLog.objects.filter(utilizador_id=user_id).all()
        self.assertEqual(len(all_logs), 1)
        self.assertEqual(all_logs[0].status, ManualChangeStatus.APPROVED.value)

        # We shouldn't have that open request anymore
        requested_all = StockForecastOpenRequest.objects.filter().all()
        self.assertEqual(len(requested_all), 0)

    def test_declining_change_will_prevent_changes_to_forecast(self):
        """"""
        # setup
        user_id = 678
        new_qty = 14321
        target_date = datetime.now(tz=timezone.utc) + relativedelta(months=5)
        request = self.stub_forecast_request(target_date=target_date, new_qty=new_qty)

        # Execution
        params = ConfirmRequestParams(
            **self.filters,
            status=ManualChangeStatus.DECLINED.value,
            request_id=request.id,
            utilizador_id=user_id,
            utilizador="employee of the month",
            comentario="a random comment to request this",
        )
        confirm_stock_change_request(params=params)

        # Verify
        # (We are not loading fixtures, so we shouldn't have anything else in the DB for this test)
        forecasted = StockForecast.objects.filter(
            ano=target_date.year,
            mes=target_date.month,
        ).first()

        self.assertEqual(forecasted.qt_u, 500)
        self.assertEqual(forecasted.qt_cx, 500)
        self.assertEqual(forecasted.qt_cx9, 500)

        # We still need to have a log with the decision though
        all_logs = ForecastManualChangeLog.objects.filter(utilizador_id=user_id).all()
        self.assertEqual(len(all_logs), 1)
        self.assertEqual(all_logs[0].status, ManualChangeStatus.DECLINED.value)

        # We shouldn't have that open request anymore
        requested_all = StockForecastOpenRequest.objects.filter().all()
        self.assertEqual(len(requested_all), 0)

    def test_making_a_decision_will_log_and_link_to_the_original_request(self):
        """"""
        # setup
        user = "employee of the month"
        comentario = "a random comment to request this"
        user_id = 678
        new_qty = 14321
        target_date = datetime.now(tz=timezone.utc) + relativedelta(months=5)
        request = self.stub_forecast_request(target_date=target_date, new_qty=new_qty)

        # sanity check
        requested_all = StockForecastOpenRequest.objects.filter().all()
        self.assertEqual(len(requested_all), 1)

        # Execution
        params = ConfirmRequestParams(
            **self.filters,
            status=ManualChangeStatus.APPROVED.value,
            request_id=request.id,
            utilizador_id=user_id,
            utilizador=user,
            comentario=comentario,
        )
        confirm_stock_change_request(params=params)

        # We should have only one log from the user here. since this is a test with no fixtures loaded.
        all_logs = ForecastManualChangeLog.objects.filter(utilizador_id=user_id).all()

        self.assertEqual(len(all_logs), 1)

        final_log = all_logs[0]
        original_log = cast(ForecastManualChangeLog, final_log.parent_request)
        if not original_log:
            raise Exception("we need a parent request here")

        self.assertEqual(final_log.status, ManualChangeStatus.APPROVED.value)
        self.assertEqual(final_log.utilizador_id, user_id)
        self.assertEqual(original_log.status, ManualChangeStatus.REQUESTED.value)
        self.assertEqual(float(original_log.qt_u), final_log.qt_u)
        self.assertEqual(float(original_log.qt_cx), final_log.qt_cx)
        self.assertEqual(float(original_log.qt_cx9), final_log.qt_cx9)
