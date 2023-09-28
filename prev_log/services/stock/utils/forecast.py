import calendar
from datetime import date
from typing import Any, Dict, cast

from dateutil.relativedelta import relativedelta

from prev_log.models import OpenOrder, OrigemPrevisao, Stock, StockForecast
from prev_log.pydantic_model.product import ProductIdentification
from prev_log.services.stock.utils.aggregate import merge_stock_data
from prev_log.services.utils.filters import filter_future, filter_past
from prev_log.services.utils.indexes import generate_index, generate_index_from_int

# Number of months in the future (including current) that we should make a forecast for
STOCK_FORECAST_RANGE = 19


def calculate_stock_for_single_unit(
    current_stock: float,
    open_orders: Dict[str, float],
    sales: Dict[str, float],
):
    """
    Calculate the stock forecast for the current month
    and the 18 following
    """
    forecast = {}

    curr_date = date.today()
    latest_stock = current_stock
    for offset in range(STOCK_FORECAST_RANGE):
        calculation_date = curr_date + relativedelta(months=offset)
        index = generate_index(target_date=calculation_date)
        month_order = open_orders.get(index, 0)
        month_sale = sales.get(index, 0)

        new_stock = latest_stock + month_order - month_sale
        if new_stock < 0:
            new_stock = 0

        forecast[index] = new_stock
        latest_stock = new_stock

    return forecast


def get_this_month_stock(filters: ProductIdentification) -> Dict[str, Any]:
    # date range
    current_date = date.today()
    day_range = calendar.monthrange(year=current_date.year, month=current_date.month)
    start_date = date(
        year=current_date.year, month=current_date.month, day=day_range[0]
    )
    end_date = date(year=current_date.year, month=current_date.month, day=day_range[1])

    data = Stock.objects.filter(
        **filters.dict(),
        dia__range=(start_date, end_date),
    ).values()

    aggregated = merge_stock_data(data)
    index = generate_index(target_date=current_date)

    empty_stock = {
        "last_day": 0,
        "u": 0,
        "cx": 0,
        "cx9": 0,
    }
    return aggregated.get(index, empty_stock)


def serialize_orders(filters: ProductIdentification) -> Dict[str, Any]:
    db_objects = (
        OpenOrder.objects.filter(
            **filters.dict(),
        )
        .filter(
            filter_future(),
        )
        .all()
    )

    orders = {"u": {}, "cx": {}, "cx9": {}}
    for order_item in db_objects:
        index = generate_index_from_int(month=order_item.mes, year=order_item.ano)

        orders["u"][index] = float(order_item.qt_u)
        orders["cx"][index] = float(order_item.qt_cx)
        orders["cx9"][index] = float(order_item.qt_cx9)

    return orders


def update_stock_forecast(
    filters: ProductIdentification,
    sales: Dict[str, Dict[int, float]],
):
    """
    This calculates the stock forecast for a given product.
    The results are calculated as u, cx and cx9
    """
    current_date = date.today()

    # Get current stock data
    current_stock = get_this_month_stock(filters=filters)
    # Get Open orders
    orders = serialize_orders(filters=filters)

    # Make the forecast
    stock_forecast = {
        "u": calculate_stock_for_single_unit(
            current_stock=current_stock["u"],
            open_orders=orders["u"],
            sales=sales["u"],
        ),
        "cx": calculate_stock_for_single_unit(
            current_stock=current_stock["cx"],
            open_orders=orders["cx"],
            sales=sales["cx"],
        ),
        "cx9": calculate_stock_for_single_unit(
            current_stock=current_stock["cx9"],
            open_orders=orders["cx9"],
            sales=sales["cx9"],
        ),
    }

    # Save in the DB
    for offset in range(STOCK_FORECAST_RANGE):
        target_date = current_date + relativedelta(months=offset)
        index = generate_index(target_date=target_date)

        origem_auto = OrigemPrevisao.objects.filter(
            designacao=OrigemPrevisao.AUTO
        ).first

        stock_filters = {
            **filters.dict(),
            "ano": target_date.year,
            "mes": target_date.month,
        }
        [month_forecast, _] = StockForecast.objects.get_or_create(
            **stock_filters, defaults={"origem": origem_auto}
        )

        # We don't want to save when input is not automatic
        forecast_origin = cast(OrigemPrevisao, month_forecast.origem)
        if forecast_origin.designacao == OrigemPrevisao.AUTO:
            month_forecast.qt_u = stock_forecast["u"][index]
            month_forecast.qt_cx = stock_forecast["cx"][index]
            month_forecast.qt_cx9 = stock_forecast["cx9"][index]
            month_forecast.save()

    # delete previous months forecasts
    StockForecast.objects.filter(
        **filters.dict(),
    ).filter(
        filter_past(),
    ).delete()

    return stock_forecast
