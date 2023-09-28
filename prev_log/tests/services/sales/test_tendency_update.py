from typing import Dict

from django.test import TestCase

from prev_log.models import ForecastManualChangeLog, OrigemPrevisao, Tendency
from prev_log.pydantic_model.sale import TendencyChangeRequestParams
from prev_log.services.sales.update import update_anual_base_tendency
from prev_log.services.utils.log import LogForecastOrigin, ManualChangeStatus
from prev_log.tests.factory.sales import TendencyFactory


class TendencyAnualBaseChangeTestCase(TestCase):
    """Tendency Calcualtion Unit Tests"""

    filters: Dict[str, str]

    def setUp(self):
        filters = {
            "familia": "familia_teste",
            "bo": "bo_teste",
            "artigo": "artigo_teste",
            "empresa": "CO",
        }
        self.filters = filters

        OrigemPrevisao.objects.create(designacao=OrigemPrevisao.AUTO)
        OrigemPrevisao.objects.create(designacao=OrigemPrevisao.MANUAL)

        TendencyFactory(**filters, base_anual=0.7644)

    def test_will_create_new_tendency_if_not_exists(self):
        """"""
        user_id = 678
        utilizador = "employee of the month"
        filters = {
            "familia": "familia_teste_nao_existe",
            "bo": "bo_teste_nao_existe",
            "artigo": "artigo_teste_nao_existe",
            "empresa": "CO",
        }

        # Sanity Check
        tendencies = Tendency.objects.filter(**filters).all()
        self.assertEqual(len(tendencies), 0)

        # Execution
        params = TendencyChangeRequestParams(
            **filters,
            utilizador_id=user_id,
            utilizador=utilizador,
            comentario="a random comment to request this",
            base_anual=0.5,
        )
        update_anual_base_tendency(params=params)

        # Expectations
        tendencies = Tendency.objects.filter(**filters).all()
        self.assertEqual(len(tendencies), 1)

    def test_will_create_a_log_of_the_event(self):
        """"""
        user_id = 678
        utilizador = "employee of the month"
        base_anual = 0.5

        # Execution
        params = TendencyChangeRequestParams(
            **self.filters,
            utilizador_id=user_id,
            utilizador=utilizador,
            comentario="a random comment to request this",
            base_anual=base_anual,
        )
        update_anual_base_tendency(params=params)
        log = ForecastManualChangeLog.objects.filter(**self.filters).first()
        if not log:
            raise Exception("That is unexpected")

        self.assertEqual(float(log.qt_u), base_anual)
        self.assertEqual(float(log.prev_qt_u), 0.7644)
        self.assertEqual(log.origem_forecast, LogForecastOrigin.TENDENCY.value)
        self.assertEqual(log.status, ManualChangeStatus.APPROVED.value)
        self.assertEqual(log.utilizador_id, user_id)
        self.assertEqual(log.utilizador, utilizador)

    def test_will_update_the_tendency(self):
        """"""
        user_id = 678
        utilizador = "employee of the month"
        base_anual = 0.5

        # Execution
        params = TendencyChangeRequestParams(
            **self.filters,
            utilizador_id=user_id,
            utilizador=utilizador,
            comentario="a random comment to request this",
            base_anual=base_anual,
        )
        update_anual_base_tendency(params=params)

        tendency = Tendency.objects.filter(**self.filters).first()
        if not tendency:
            raise Exception("that is unexpected")

        self.assertEqual(float(tendency.base_anual), base_anual)
