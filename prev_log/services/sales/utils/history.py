from collections import defaultdict
from typing import Any, Dict, Literal

from prev_log.models import Sale
from prev_log.pydantic_model.product import ProductIdentification
from prev_log.services.utils.filters import filter_two_years_ago
from prev_log.services.utils.indexes import generate_index_from_int
from prev_log.services.utils.products import get_product_key


def convert_sales_to_history_hash(objects: list):
    result = defaultdict(dict)
    for sale_item in objects:
        key = get_product_key(
            family=sale_item["familia"],
            article=sale_item["artigo"],
            bo=sale_item["bo"],
            company=sale_item["empresa"],
        )
        index = generate_index_from_int(
            year=sale_item["ano"],
            month=sale_item["mes"],
        )
        result[key][index] = {
            "u": sale_item["qt_u"],
            "cx": sale_item["qt_cx"],
            "cx9": sale_item["qt_cx9"],
        }

    return result


def get_sales_history(filters: ProductIdentification):
    objects = (
        Sale.objects.filter(
            **filters.dict(),
        )
        .filter(filter_two_years_ago())
        .values()
    )

    full_hash = convert_sales_to_history_hash(objects=objects)
    product_key = get_product_key(
        family=filters.familia,
        bo=filters.bo,
        company=filters.empresa,
        article=filters.artigo,
    )
    return full_hash[product_key]


def translate_history_qty_unit(
    sales_history: Dict[str, Any], unit: Literal["u", "cx", "cx9"]
):
    history_qt = {}

    for sale_index, qt in sales_history.items():
        history_qt[sale_index] = float(qt[unit])

    return history_qt
