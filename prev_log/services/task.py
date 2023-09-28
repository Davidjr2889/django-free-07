from prev_log.models import Product, Tendency
from prev_log.pydantic_model.product import ProductIdentification
from prev_log.services.purchase.utils.forecast import calculate_purchase_forecast
from prev_log.services.sales.utils.forecast import update_sales_forecast
from prev_log.services.sales.utils.history import (
    get_sales_history,
    translate_history_qty_unit,
)
from prev_log.services.sales.utils.tendency import calculate_new_tendency
from prev_log.services.stock.utils.forecast import update_stock_forecast


def update_product_forecast(product: Product):
    filters = ProductIdentification(
        empresa=product.empresa,
        bo=product.bo,
        familia=product.familia,
        artigo=product.artigo,
    )

    [tendency, _] = Tendency.objects.get_or_create(
        **filters.dict(),
    )

    # If we don't have the base anual value, there's no point proceeding
    if not tendency.base_anual or tendency.base_anual == 0:
        tendency.base_anual = 0
        tendency.save()
        return

    # Calculate new tendencies
    raw_sales_history = get_sales_history(filters=filters)
    sale_history = translate_history_qty_unit(raw_sales_history, unit="u")

    new_tendency = calculate_new_tendency(history=sale_history)

    tendency.media_trimestral = new_tendency.average_trimester
    tendency.tendencia_trimestral = new_tendency.tendency_trimester
    tendency.media_anual = new_tendency.average_anual
    tendency.tendencia_anual = new_tendency.tendency_anual
    tendency.save()

    # Calculate new sales forecast
    sale_forecast = update_sales_forecast(
        filters=filters,
        base_anual=tendency.base_anual,
    )

    # Calculate new stock forecast
    stock_forecast = update_stock_forecast(
        filters=filters,
        sales=sale_forecast,
    )

    # Last, but not least, update purchase forecast
    calculate_purchase_forecast(
        product=product,
        stock=stock_forecast,
    )
