from collections import defaultdict
from typing import Any, List

from prev_log.models import BasicAgreement, OpenOrder
from prev_log.services.utils.filters import filter_future
from prev_log.services.utils.indexes import generate_index
from prev_log.services.utils.products import (
    aggreagate_by_product,
    get_all_products,
    get_product_key,
    product_base_data,
)


def get_agreement():
    queryset = BasicAgreement.objects.filter(
        filter_future(),
    )

    return queryset.values()


def get_open_orders():
    queryset = OpenOrder.objects.filter(
        filter_future(),
    )

    return queryset.values()


def aggregate_by_year_month(target: List[Any]):
    if not target:
        return {}

    aggregated = {}
    for item in target:
        index = generate_index(item["previsao_data_entrega"])

        if not aggregated.get(index):
            aggregated[index] = {
                "u": 0,
                "cx": 0,
                "cx9": 0,
            }

        aggregated[index]["u"] += float(item["qt_u"])
        aggregated[index]["cx"] += float(item["qt_cx"])
        aggregated[index]["cx9"] += float(item["qt_cx9"])

    return aggregated


def list_orders(user_id):
    products = get_all_products(user_id)

    raw_agreement_data = get_agreement()
    agreegated_agreement = aggreagate_by_product(
        products=products,
        target=raw_agreement_data,
    )

    raw_open_order_data = get_open_orders()
    agreegated_open_order = aggreagate_by_product(
        products=products,
        target=raw_open_order_data,
    )

    lista_familia = defaultdict(list)
    for product_item in products:
        familia = product_item["familia"]

        key = get_product_key(
            family=familia,
            article=product_item["artigo"],
            company=product_item["empresa"],
            bo=product_item["bo"],
        )
        target_agreement = agreegated_agreement.get(key)
        target_order = agreegated_open_order.get(key)

        product_data = product_base_data(product=product_item)
        product_data["agreement"] = aggregate_by_year_month(target=target_agreement)
        product_data["orders"] = aggregate_by_year_month(target=target_order)

        lista_familia[familia].append(product_data)

    return lista_familia
