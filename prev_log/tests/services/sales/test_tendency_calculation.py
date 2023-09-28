from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from prev_log.services.sales.utils.tendency import calculate_new_tendency


class TendencyCalculationTestCase(TestCase):
    """Tendency Calcualtion Unit Tests"""

    def generate_random_sales_data(self):
        history = {}

        current_date = datetime.now()
        values = [
            100,
            #
            120,
            480,
            720,
            100,
            400,
            500,
            600,
            200,
            100,
            90,
            120,
            140,
            #
            100,
            300,
            600,
            230,
            120,
            510,
            330,
            740,
            350,
            440,
            230,
            50,
        ]

        for i in range(25):
            date_key = int(current_date.strftime("%Y%m"))

            history[date_key] = values[i]

            current_date -= relativedelta(months=1)

        return history

    def test_tendencies_are_calculated_correctly(self):
        """
        - Deverá ser calculado:
        average_trimester
        tendency_trimester
        average_anual
        tendency_anual
        weighted_tendency

        - Deverá ser copiado do produto:
        base_anual
        """
        history = self.generate_random_sales_data()
        # Valores esperados para o cálculo manual

        expected_average_trimester = 440
        expected_tendency_trimester = 0.32

        # would originally be 297.5... but how to sell 0.5?
        expected_average_anual = 297
        expected_tendency_anual = -0.1075

        expected_weighted_tendency = 0.0635

        calculated_tendency = calculate_new_tendency(history)

        self.assertEqual(
            expected_average_trimester,
            calculated_tendency.average_trimester,
        )

        self.assertEqual(
            expected_tendency_trimester,
            calculated_tendency.tendency_trimester,
        )

        self.assertEqual(
            expected_average_anual,
            calculated_tendency.average_anual,
        )

        self.assertEqual(
            expected_tendency_anual,
            calculated_tendency.tendency_anual,
        )

        self.assertEqual(
            expected_weighted_tendency,
            calculated_tendency.weighted_tendency,
        )
