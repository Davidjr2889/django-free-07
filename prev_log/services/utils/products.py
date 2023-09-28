from collections import defaultdict
from typing import Any, Dict, List

from backoffice.models import UserDataPerm
from prev_log.models import Product


def get_product_key(
    family: str,
    article: str,
    company: str,
    bo: str,
):
    return f"{family}-{article}-{company}-{bo}"


def get_all_products(user_id):
    queryset = UserDataPerm.get_safe_qs(Product.objects, user_id).all()
    return queryset.values()


def aggreagate_by_product(
    products: Dict[str, Any],
    target: List[Dict[str, Any]],
):
    aggregated = defaultdict(list)

    for single_product in products:
        key = get_product_key(
            family=single_product["familia"],
            article=single_product["artigo"],
            company=single_product["empresa"],
            bo=single_product["bo"],
        )

        aggregated[key] = [
            item
            for item in target
            if single_product["familia"] == item["familia"]
            and single_product["artigo"] == item["artigo"]
            and single_product["empresa"] == item["empresa"]
            and single_product["bo"] == item["bo"]
        ]

    return aggregated


def product_base_data(
    product: Dict[str, Any],
):
    return {
        "id": product["id"],
        "empresa": product["empresa"],
        "bo": product["bo"],
        "family": product["familia"],
        "artigo": product["artigo"],
        "descricao": product["descricao"],
        "planning": product["planingsys"],
        "min_ord_qty": product["min_ordr_qty"],
        "ord_mult": product["ordr_multi"],
        "stock": product["stock_actual"],
        "stock_min": product["stock_minimo"],
        "stock_reservado": product["stock_reservado"],
        "stock_encomendado": product["stock_encomendado"],
        "lead_time": product["lead_time"],
    }


class BaseProductListing:
    def get_product(self, user_id):
        return get_all_products(user_id)

    def get_product_key(
        self,
        family: str,
        article: str,
        company: str,
        bo: str,
    ):
        return get_product_key(
            family=family,
            article=article,
            company=company,
            bo=bo,
        )

    def aggregate(
        self,
        products: Dict[str, Any],
        target: List[Dict[str, Any]],
    ):
        return aggreagate_by_product(
            products=products,
            target=target,
        )

    def product_base_data(
        self,
        product: Dict[str, Any],
    ):
        return product_base_data(product=product)
