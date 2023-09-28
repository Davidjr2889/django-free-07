from datetime import date

from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings

from prev_log.models import (
    OrigemPrevisao,
    PurchaseForecast,
    SaleForecast,
    StockForecast,
)
from prev_log.pydantic_model.product import ProductIdentification
from prev_log.services.purchase.utils.forecast import PURCHASE_FORECAST_RANGE
from prev_log.services.sales.utils.forecast import SALES_FORECAST_RANGE
from prev_log.services.stock.utils.forecast import STOCK_FORECAST_RANGE
from prev_log.tasks import (
    task_update_all_forecasts,
    task_update_single_product_forecasts,
)
from prev_log.tests.factory import ProductFactory
from prev_log.tests.factory.sales import SaleFactory, TendencyFactory


class CeleryTasksTestCase(TestCase):
    """Tendency Calcualtion Unit Tests"""

    filter_1: ProductIdentification
    filter_2: ProductIdentification

    def create_product(
        self, filters: ProductIdentification, apply_tendency: bool = True
    ):
        # Setup
        ProductFactory(
            **filters.dict(),
            lead_time=35,
            min_ordr_qty=50,
            ordr_multi=2,
            stock_minimo=349,
            stock_actual=1000,
            stock_reservado=300,
            stock_encomendado=400,
        )

        if apply_tendency:
            TendencyFactory(
                **filters.dict(),
                base_anual=0.5,
            )

        curr_date = date.today()
        for offset in range(25):
            target_date = curr_date + relativedelta(months=offset - 24)
            qty = 500

            if offset == 24:
                qty = 0

            SaleFactory(
                **filters.dict(),
                ano=target_date.year,
                mes=target_date.month,
                qt_u=qty,
                qt_cx=qty,
                qt_cx9=qty,
            )

    def setUp(self):
        filters = {
            "familia": "familia_teste",
            "bo": "bo_teste",
            "artigo": "artigo_teste",
            "empresa": "CO",
        }
        self.filter_1 = ProductIdentification.parse_obj(filters)
        self.create_product(self.filter_1)

        filters["artigo"] = "second"
        self.filter_2 = ProductIdentification.parse_obj(filters)
        self.create_product(self.filter_2)

        OrigemPrevisao.objects.create(designacao=OrigemPrevisao.AUTO)
        OrigemPrevisao.objects.create(designacao=OrigemPrevisao.MANUAL)

    def make_empty_product_check(self, target_filter: ProductIdentification):
        stock = StockForecast.objects.filter(
            **target_filter.dict(),
        ).all()
        self.assertEqual(len(stock), 0)

        sale = SaleForecast.objects.filter(
            **target_filter.dict(),
        ).all()
        self.assertEqual(len(sale), 0)

        purchase = PurchaseForecast.objects.filter(
            **target_filter.dict(),
        ).all()
        self.assertEqual(len(purchase), 0)

    def make_product_assertions(self, target_filter: ProductIdentification):
        stock = StockForecast.objects.filter(
            **target_filter.dict(),
        ).all()
        self.assertEqual(len(stock), STOCK_FORECAST_RANGE)

        sale = SaleForecast.objects.filter(
            **target_filter.dict(),
        ).all()
        self.assertEqual(len(sale), SALES_FORECAST_RANGE)

        purchase = PurchaseForecast.objects.filter(
            **target_filter.dict(),
        ).all()
        self.assertEqual(len(purchase), PURCHASE_FORECAST_RANGE)

    @override_settings(
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        CELERY_ALWAYS_EAGER=True,
        BROKER_BACKEND="memory",
    )
    def test_update_all_products_will_create_all_forecasts(self):
        """"""
        # Sanity Check
        self.make_empty_product_check(target_filter=self.filter_1)
        self.make_empty_product_check(target_filter=self.filter_2)

        task = task_update_all_forecasts.apply()

        self.assertEqual(task.status, "SUCCESS")
        self.make_product_assertions(target_filter=self.filter_1)
        self.make_product_assertions(target_filter=self.filter_2)

    def test_company_is_unique_in_the_forecasting_models(self):
        # Replicate product 1 with only company different
        filter_3 = self.filter_1.copy()
        filter_3.empresa = "AC"
        self.create_product(filters=filter_3)

        # Sanity Check
        self.make_empty_product_check(target_filter=self.filter_1)
        self.make_empty_product_check(target_filter=self.filter_2)
        self.make_empty_product_check(target_filter=filter_3)

        task = task_update_all_forecasts.apply()

        self.assertEqual(task.status, "SUCCESS")
        self.make_product_assertions(target_filter=self.filter_1)
        self.make_product_assertions(target_filter=self.filter_2)
        self.make_product_assertions(target_filter=filter_3)

    @override_settings(
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        CELERY_ALWAYS_EAGER=True,
        BROKER_BACKEND="memory",
    )
    def test_update_single_product_works_as_expected(self):
        """"""
        # Sanity Check
        self.make_empty_product_check(target_filter=self.filter_1)
        self.make_empty_product_check(target_filter=self.filter_2)

        task = task_update_single_product_forecasts.apply(
            args=[
                self.filter_1.empresa,
                self.filter_1.bo,
                self.filter_1.familia,
                self.filter_1.artigo,
            ]
        )

        self.assertEqual(task.status, "SUCCESS")
        self.make_product_assertions(target_filter=self.filter_1)
        self.make_empty_product_check(target_filter=self.filter_2)

    @override_settings(
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        CELERY_ALWAYS_EAGER=True,
        BROKER_BACKEND="memory",
    )
    def test_empty_anual_base_will_skip_task(self):
        """"""
        # setup
        filters = {
            "familia": "familia_empty_teste",
            "bo": "bo_teste",
            "artigo": "artigo__empty_teste",
            "empresa": "CO",
        }
        empty_tendency_filter = ProductIdentification.parse_obj(filters)
        self.create_product(
            empty_tendency_filter,
            apply_tendency=False,
        )

        # Sanity Check
        self.make_empty_product_check(target_filter=empty_tendency_filter)

        task = task_update_all_forecasts.apply()

        self.assertEqual(task.status, "SUCCESS")
        self.make_empty_product_check(target_filter=empty_tendency_filter)
