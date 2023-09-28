from datetime import date

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from prev_log.services.sales.utils.forecast import (
    SALES_FORECAST_RANGE,
    calculate_sale_forecast,
)
from prev_log.services.utils.indexes import generate_index


class SaleForecastCalculationTestCase(TestCase):
    """Tendency Calcualtion Unit Tests"""

    def test_will_yield_values_starting_12_months_ago(self):
        """"""
        # execução
        result = calculate_sale_forecast(anual_base_trend=0.5, history={})
        self.assertEqual(len(result), SALES_FORECAST_RANGE)

        current_date = date.today()
        for offset in range(12):
            offset_date = current_date + relativedelta(months=(offset - 12))
            offset_index = generate_index(offset_date)

            self.assertIsNotNone(result.get(offset_index))

        # for the 13th month ago it should be none
        offset_date = current_date + relativedelta(months=-13)
        offset_index = generate_index(offset_date)
        self.assertIsNone(result.get(offset_index))

    def test_will_yield_values_up_to_the_next_18_months(self):
        """"""
        result = calculate_sale_forecast(anual_base_trend=0.5, history={})
        self.assertEqual(len(result), SALES_FORECAST_RANGE)

        current_date = date.today()
        for offset in range(19):
            offset_date = current_date + relativedelta(months=offset)
            offset_index = generate_index(offset_date)
            self.assertIsNotNone(result.get(offset_index))

        # for the 19th month it should be none
        offset_date = current_date + relativedelta(months=19)
        offset_index = generate_index(offset_date)

        self.assertIsNone(result.get(offset_index))

    def test_will_calculate_when_anual_base_exists_and_product_has_enough_data(self):
        """
        Vamos calcular aqui para os 18 meses futuros.
        Para isto:
        1. devemos ter tendencia anual base
        2. O produto deve ter dados de pelo menos 12 meses
        """
        # Current month
        curr_date = date.today()
        current_month_index = generate_index(curr_date)

        # Seed: Last Year
        last_year = curr_date + relativedelta(months=(-12))
        last_year_index = generate_index(last_year)
        # Seed: Last Year, next month
        last_year_next_month = curr_date + relativedelta(months=(-11))
        last_year_next_month_index = generate_index(last_year_next_month)

        # Analysis: Next Month
        next_month_date = curr_date + relativedelta(months=1)
        next_month_index = generate_index(next_month_date)
        # Analysis: Next Month of current year
        current_month_next_year = curr_date + relativedelta(months=12)
        current_month_next_year_index = generate_index(current_month_next_year)
        # Analysis: Next Month of next year
        next_year_next_month = curr_date + relativedelta(months=13)
        next_year_next_month_index = generate_index(next_year_next_month)

        # Gerar historico de vendas
        base_anual = 0.25
        history = {
            current_month_index: 10,
            last_year_index: 200,
            last_year_next_month_index: 300,
        }

        # execução
        result = calculate_sale_forecast(anual_base_trend=base_anual, history=history)
        self.assertEqual(len(result), SALES_FORECAST_RANGE)

        # Expectations
        forecast_month_current = 240
        forecast_month_next = 375
        forecast_next_year_current_month = 312.5
        forecast_next_year_next_month = 468.75

        # verificação
        self.assertEqual(forecast_month_current, result[current_month_index])
        self.assertEqual(forecast_month_next, result[next_month_index])
        self.assertEqual(
            forecast_next_year_current_month,
            result[current_month_next_year_index],
        )

        self.assertEqual(
            forecast_next_year_next_month,
            result[next_year_next_month_index],
        )
