from datetime import date
from typing import Dict, cast

from dateutil.relativedelta import relativedelta

from prev_log.models import OrigemPrevisao, SaleForecast
from prev_log.pydantic_model.product import ProductIdentification
from prev_log.services.utils.filters import filter_over_two_years_in_past
from prev_log.services.utils.indexes import generate_index

from .history import get_sales_history, translate_history_qty_unit

SALES_FORECAST_RANGE = 12 + 18 + 1  # 12 months ago, 18 mnths ahead + current month


def calculate_sale_forecast(
    anual_base_trend: float,
    history: Dict[int, float],
) -> Dict[int, float]:
    """
    Calcula a previsão de vendas para os próximos 18 mêses de um determinado produto.
    Utiliza o histórico de vendas de 02 anos atrás e a tendencia calculada com a anual base.

    Se houver tendencia anual base, utiliza ela. Se não houver, pula o cálculo.
    (Este método será invocado quando o utilizador alterar a tendencia anual base!)

    Meses homólogos devem ser utilizados
    (sempre relacionados ao mes passado ao preiodo de cálculo)
    """
    growth = 1 + anual_base_trend
    history_copy = {**history}
    forecast = {}

    today = date.today()
    current_index = generate_index(today)

    # Cálculo dos 12 meses atrás, dos próximos 18 meses + o mes atual
    for offset in range(SALES_FORECAST_RANGE):
        month_offset = offset - 12  # We need to start 12 months ago
        forecast_date = date.today() + relativedelta(months=month_offset)
        forecast_index = generate_index(forecast_date)

        history_date = date.today() + relativedelta(months=(month_offset - 12))
        history_index = generate_index(history_date)

        try:
            # Para o mês atual, subtrai da previsao as vendas já realizadas
            if forecast_index == current_index:
                forecast[current_index] = (
                    history_copy[history_index] * growth - history_copy[current_index]
                )
                # Forecast must always be positive
                if forecast[current_index] < 0:
                    forecast[current_index] = 0

                history_copy[current_index] += forecast[current_index]
                continue

            # Para os próximos meses, não existem vendas já realizadas,
            # mas para os anteriores, já existe
            forecasted = history_copy[history_index] * growth

            if forecast_index > current_index:
                history_copy[forecast_index] = forecasted

            forecast[forecast_index] = forecasted

        except (TypeError, KeyError):
            forecast[forecast_index] = 0

    return forecast


def simulate_updated_sales_forecast(
    filters: ProductIdentification,
    base_anual: float,
):
    """This is a simulation and does not take into account the origin"""
    sales_history = get_sales_history(filters=filters)

    history_u = translate_history_qty_unit(sales_history, unit="u")
    history_cx = translate_history_qty_unit(sales_history, unit="cx")
    history_cx9 = translate_history_qty_unit(sales_history, unit="cx9")

    forecast = {
        "u": calculate_sale_forecast(base_anual, history_u),
        "cx": calculate_sale_forecast(base_anual, history_cx),
        "cx9": calculate_sale_forecast(base_anual, history_cx9),
    }

    return forecast


def translated_sale_forecast_simulation(forecasted: Dict[str, Dict[int, float]]):
    translated = {}
    curr_date = date.today()

    for offset in range(SALES_FORECAST_RANGE):
        month_offset = offset - 12
        calculation_date = curr_date + relativedelta(months=month_offset)
        index = generate_index(calculation_date)

        translated[index] = {
            "u": forecasted["u"][index],
            "cx": forecasted["cx"][index],
            "cx9": forecasted["cx9"][index],
        }

    return translated


def update_sales_forecast(
    filters: ProductIdentification,
    base_anual: float,
):
    curr_date = date.today()

    forecast = simulate_updated_sales_forecast(
        filters=filters,
        base_anual=base_anual,
    )

    origem_auto = OrigemPrevisao.objects.filter(designacao=OrigemPrevisao.AUTO).first()

    for offset in range(SALES_FORECAST_RANGE):
        month_offset = offset - 12
        calculation_date = curr_date + relativedelta(months=month_offset)
        index = generate_index(calculation_date)

        [sale_forecast, _] = SaleForecast.objects.get_or_create(
            **filters.dict(),
            ano=calculation_date.year,
            mes=calculation_date.month,
            defaults={"origem": origem_auto},
        )
        sale_forecast = cast(SaleForecast, sale_forecast)
        forecast_origin = cast(OrigemPrevisao, sale_forecast.origem)

        if forecast_origin.designacao == OrigemPrevisao.AUTO:
            sale_forecast.qt_u = forecast["u"][index]
            sale_forecast.qt_cx = forecast["cx"][index]
            sale_forecast.qt_cx9 = forecast["cx9"][index]

            sale_forecast.save()

    SaleForecast.objects.filter(
        **filters.dict(),
    ).filter(
        filter_over_two_years_in_past(),
    ).delete()

    return forecast
