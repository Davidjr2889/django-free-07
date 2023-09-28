from collections import defaultdict

from prev_log.models import Purchase, PurchaseForecast
from prev_log.services.purchase.utils.aggregate import merge_purchase_data
from prev_log.services.utils.products import BaseProductListing


class PurchaseViewSet(BaseProductListing):
    def get_purchase(self):
        return Purchase.objects.values()

    def get_purchase_forecast(self):
        return PurchaseForecast.objects.values()

    def list(self, user_id):
        lista_familia = defaultdict(list)
        products = self.get_product(user_id)

        history_purchase = self.aggregate(
            products=products,
            target=self.get_purchase(),
        )

        forecast_purchase = self.aggregate(
            products=products,
            target=self.get_purchase_forecast(),
        )

        for product_item in products:
            familia = product_item["familia"]

            product_key = self.get_product_key(
                family=product_item["familia"],
                article=product_item["artigo"],
                company=product_item["empresa"],
                bo=product_item["bo"],
            )

            purchase_forecast = {}
            if forecast_purchase[product_key]:
                purchase_forecast = {
                    (f"{item['ano']}{item['mes']:02d}"): {
                        "u": item["qt_u"],
                        "cx": item["qt_cx"],
                        "cx9": item["qt_cx9"],
                    }
                    for item in forecast_purchase[product_key]
                }

            product_data = {
                **self.product_base_data(product_item),
                "history": merge_purchase_data(history_purchase[product_key]),
                "forecast": purchase_forecast,
            }

            lista_familia[familia].append(product_data)

        return lista_familia
