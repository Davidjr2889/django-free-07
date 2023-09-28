import math
from datetime import date, datetime, time, timezone
from typing import Dict, cast

from dateutil.relativedelta import relativedelta
from django.forms.models import model_to_dict

from prev_log.models import OrigemPrevisao, Product, PurchaseForecast
from prev_log.pydantic_model.product import ProductIdentification
from prev_log.pydantic_model.qty import PurchaseEntryQty, QtyRatios
from prev_log.services.utils.filters import filter_past
from prev_log.services.utils.indexes import generate_index

PURCHASE_FORECAST_RANGE = 19  # 1 18months + current


def parse_to_datetime(date: date) -> datetime:
    return datetime.combine(
        date=date,
        time=time(),
        tzinfo=timezone.utc,
    )


def calculate_purchase_forecast(
    product: Product,
    stock: Dict[str, Dict[int, float]],
):
    filters = ProductIdentification(**model_to_dict(product))
    lead_time = product.lead_time or 0
    min_qty = product.min_ordr_qty or 0
    multiple_of = product.ordr_multi or 1

    ratios = QtyRatios.from_entry(entry=stock)
    unit_stock = stock["u"]

    forecasted: Dict[int, PurchaseEntryQty] = {}
    curr_date = date.today()
    for offset in range(PURCHASE_FORECAST_RANGE):
        target_date = curr_date + relativedelta(months=offset)
        target_index = generate_index(target_date=target_date)

        order_date = target_date - relativedelta(days=lead_time)
        order_index = generate_index(order_date)

        forecasted[target_index] = PurchaseEntryQty(
            order_date=parse_to_datetime(target_date),
        )
        order_amount = product.stock_minimo - unit_stock[target_index]

        # Stock is above minimum
        if order_amount < 0:
            continue

        # Here is where we'll store the forecast so it arrives by target date
        if not forecasted.get(order_index):
            forecasted[order_index] = PurchaseEntryQty(
                order_date=parse_to_datetime(order_date),
            )

        forecasted[order_index].u += order_amount
        forecasted[order_index].order_date = parse_to_datetime(order_date)

    # We need to rerun the loop to adjust the orders quantities and be compliant to the
    # minimum order and multiple qty
    origin = OrigemPrevisao.objects.filter(designacao=OrigemPrevisao.AUTO).first()
    for forecast_value in forecasted.values():
        revised_amount = forecast_value.u
        month = forecast_value.order_date.month
        year = forecast_value.order_date.year

        # Let's apply the minimum order qty to the amount
        if 0 < revised_amount < min_qty:
            revised_amount = min_qty

        # Let's apply the multiple of qty to the amount
        if (revised_amount > 0) and (revised_amount % multiple_of) != 0:
            multiplier: int = math.ceil(revised_amount / multiple_of)
            revised_amount: int = multiple_of * multiplier

        # Update forecast in DB
        [pontual_forecast, _] = PurchaseForecast.objects.get_or_create(
            **filters.dict(),
            ano=year,
            mes=month,
            defaults={
                "origem": origin,
                "data_limite_pedido": datetime.now(tz=timezone.utc),
            },
        )
        pontual_forecast = cast(PurchaseForecast, pontual_forecast)
        forecast_origin = cast(OrigemPrevisao, pontual_forecast.origem)

        if forecast_origin.designacao == OrigemPrevisao.AUTO:
            pontual_forecast.data_limite_pedido = forecast_value.order_date
            pontual_forecast.qt_u = revised_amount
            pontual_forecast.qt_cx = round(float(revised_amount) * ratios.cx, 2)
            pontual_forecast.qt_cx9 = round(float(revised_amount) * ratios.cx9, 2)

        pontual_forecast.save()

    # Finally some cleanup
    PurchaseForecast.objects.filter(
        **filters.dict(),
    ).filter(
        filter_past(),
    ).delete()
