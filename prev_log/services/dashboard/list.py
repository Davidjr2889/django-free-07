from collections import defaultdict

from prev_log.models import Tendency
from prev_log.services.utils.products import BaseProductListing


class ProductsNotDataViewSet(BaseProductListing):
    def get_tendency(self):
        return Tendency.objects.values()

    def list(self, user_id):
        incomplete_products = defaultdict(list)

        products = self.get_product(user_id)

        raw_tendency = self.get_tendency()
        tendency = self.aggregate(products=products, target=raw_tendency)

        for product_item in products:
            familia = product_item["familia"]
            product_key = self.get_product_key(
                family=product_item["familia"],
                article=product_item["artigo"],
                company=product_item["empresa"],
                bo=product_item["bo"],
            )

            product_tendency = tendency.get(product_key, [])
            data = self.product_base_data(product_item)

            if not product_tendency or len(product_tendency) == 0:
                incomplete_products[familia].append(data)
                continue

            base_anual = product_tendency[0].get("base_anual")
            if not base_anual or base_anual == 0:
                incomplete_products[familia].append(data)
                continue

        return incomplete_products
