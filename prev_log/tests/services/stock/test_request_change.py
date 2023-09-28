from datetime import datetime, timezone
from typing import Dict

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.test import TestCase

from backoffice.models import UserDataPerm
from prev_log.exceptions import PrevLogBadRequestException
from prev_log.models import (
    ForecastManualChangeLog,
    Product,
    StockForecast,
    StockForecastOpenRequest,
)
from prev_log.pydantic_model.stock import ChangeRequestParams
from prev_log.services.stock.change import make_stock_change_request
from prev_log.services.utils.log import LogForecastOrigin, ManualChangeStatus
from prev_log.tests.factory import ProductFactory, StockForecastFactory


class StockForecastRequestChangeTestCase(TestCase):
    """Tendency Calcualtion Unit Tests"""

    product: Product
    filters: Dict[str, str]
    user_id: int

    def setUp(self):
        filters = {
            "familia": "familia_teste",
            "bo": "bo_teste",
            "artigo": "artigo_teste",
            "empresa": "CO",
        }
        self.filters = filters

        user = User.objects.create_user(
            username="test",
            email="test@foo.com",
            password="123457",
        )
        self.user_id = user.id

        UserDataPerm.objects.create(
            user=user,
            empresa=filters["empresa"],
            bo=filters["bo"],
            empresa_bo=f'{filters["empresa"]}_{filters["bo"]}',
        )

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

    def test_requesting_change_to_invalid_product_will_raise(self):
        """"""

        # Execution
        params = ChangeRequestParams(
            familia="familia_teste_inexistente",
            bo="bo_teste_inexistente",
            artigo="artigo_teste_inexistente",
            empresa="AA",
            ano=2023,
            mes=8,
            qt_u=50,
            qt_cx=100,
            qt_cx9=150,
            utilizador_id=self.user_id,
            utilizador="employee of the month",
            comentario="a random comment to request this",
        )

        with self.assertRaises(PrevLogBadRequestException) as context:
            make_stock_change_request(params=params)

        exc = context.exception
        self.assertEqual(exc.status, 400)
        self.assertEqual(exc.error, "stock change request")
        self.assertEqual(exc.details, "invalid product")

    def test_requesting_change_will_not_change_the_forecast(self):
        """"""
        target_date = datetime.now(tz=timezone.utc) + relativedelta(months=5)
        qty = 500
        StockForecastFactory(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
            qt_u=qty,
            qt_cx=qty,
            qt_cx9=qty,
        )

        # Execution
        params = ChangeRequestParams(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
            qt_u=50,
            qt_cx=100,
            qt_cx9=150,
            utilizador_id=self.user_id,
            utilizador="employee of the month",
            comentario="a random comment to request this",
        )
        make_stock_change_request(params=params)

        # Verify
        # (We are not loading fixtures, so we shouldn't have anything else in the DB for this test)
        forecasted = StockForecast.objects.filter(
            ano=target_date.year,
            mes=target_date.month,
        ).first()

        self.assertEqual(forecasted.qt_u, qty)
        self.assertEqual(forecasted.qt_cx, qty)
        self.assertEqual(forecasted.qt_cx9, qty)

    def test_requesting_change_will_add_entry_to_request_table(self):
        """"""
        target_date = datetime.now(tz=timezone.utc) + relativedelta(months=5)
        user = "employee of the month"
        comentario = "a random comment to request this"
        user_id = self.user_id

        # Sanity Check
        requested_all = StockForecastOpenRequest.objects.all()
        self.assertEqual(len(requested_all), 0)

        # Execution
        params = ChangeRequestParams(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
            qt_u=50,
            qt_cx=100,
            qt_cx9=150,
            utilizador_id=user_id,
            utilizador=user,
            comentario=comentario,
        )
        make_stock_change_request(params=params)

        # Verify
        # (We are not loading fixtures, so we shouldn't have anything else in the DB for this test)
        requested_all = StockForecastOpenRequest.objects.filter(
            ano=target_date.year,
            mes=target_date.month,
        ).all()
        self.assertEqual(len(requested_all), 1)

        request = requested_all[0]
        self.assertEqual(request.qt_u, 50)
        self.assertEqual(request.qt_cx, 100)
        self.assertEqual(request.qt_cx9, 150)
        self.assertEqual(request.utilizador, user)
        self.assertEqual(request.utilizador_id, user_id)
        self.assertEqual(request.comentario, comentario)

    def test_requesting_change_will_log_the_request(self):
        """"""
        target_date = datetime.now(tz=timezone.utc) + relativedelta(months=5)
        user = "employee of the month"
        user_id = self.user_id

        # Sanity Check
        logged_all = ForecastManualChangeLog.objects.all()
        self.assertEqual(len(logged_all), 0)

        # Execution
        params = ChangeRequestParams(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
            qt_u=50,
            qt_cx=100,
            qt_cx9=150,
            utilizador_id=user_id,
            utilizador=user,
            comentario="a random comment to request this",
        )
        make_stock_change_request(params=params)

        # Verify
        # (We are not loading fixtures, so we shouldn't have anything else in the DB for this test)
        logged_all = ForecastManualChangeLog.objects.filter(
            ano=target_date.year,
            mes=target_date.month,
        ).all()
        self.assertEqual(len(logged_all), 1)

        log_item = logged_all[0]
        self.assertEqual(log_item.qt_u, 50)
        self.assertEqual(log_item.qt_cx, 100)
        self.assertEqual(log_item.qt_cx9, 150)

        self.assertEqual(log_item.utilizador, user)
        self.assertEqual(log_item.utilizador_id, user_id)
        self.assertEqual(
            ManualChangeStatus(log_item.status),
            ManualChangeStatus.REQUESTED,
        )
        self.assertEqual(
            LogForecastOrigin(log_item.origem_forecast),
            LogForecastOrigin.STOCK,
        )

    def test_requesting_change_will_log_current_amount(self):
        """"""
        target_date = datetime.now(tz=timezone.utc) + relativedelta(months=5)
        qty = 500
        StockForecastFactory(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
            qt_u=qty,
            qt_cx=qty,
            qt_cx9=qty,
        )

        # Execution
        params = ChangeRequestParams(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
            qt_u=50,
            qt_cx=100,
            qt_cx9=150,
            utilizador_id=self.user_id,
            utilizador="employee of the month",
            comentario="a random comment to request this",
        )
        make_stock_change_request(params=params)

        # Verify
        # (We are not loading fixtures, so we shouldn't have anything else in the DB for this test)
        forecasted = ForecastManualChangeLog.objects.filter(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
        ).first()
        if not forecasted:
            raise Exception("error")

        self.assertEqual(forecasted.prev_qt_u, qty)
        self.assertEqual(forecasted.prev_qt_cx, qty)
        self.assertEqual(forecasted.prev_qt_cx9, qty)

    def test_requesting_change_will_log_current_amount_as_zero_when_there_is_no_forecast(
        self,
    ):
        """"""
        target_date = datetime.now(tz=timezone.utc) + relativedelta(months=5)

        # Execution
        params = ChangeRequestParams(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
            qt_u=50,
            qt_cx=100,
            qt_cx9=150,
            utilizador_id=self.user_id,
            utilizador="employee of the month",
            comentario="a random comment to request this",
        )
        make_stock_change_request(params=params)

        # Verify
        # (We are not loading fixtures, so we shouldn't have anything else in the DB for this test)
        forecasted = ForecastManualChangeLog.objects.filter(
            **self.filters,
            ano=target_date.year,
            mes=target_date.month,
        ).first()
        if not forecasted:
            raise Exception("error")

        self.assertEqual(forecasted.prev_qt_u, 0)
        self.assertEqual(forecasted.prev_qt_cx, 0)
        self.assertEqual(forecasted.prev_qt_cx9, 0)
