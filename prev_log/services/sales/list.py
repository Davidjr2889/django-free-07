from collections import defaultdict
from typing import Any, Dict, List, Optional

from prev_log.models import Sale, Tendency
from prev_log.services.utils.products import BaseProductListing


class SaleViewSet(BaseProductListing):
    def get_history(self):
        return Sale.objects.values()

    def get_tendency(self):
        return Tendency.objects.values()

    def extract_sales_values(self, raw_data: Optional[List[Dict[str, Any]]]):
        data = {}
        if raw_data:
            data = {
                (f"{item['ano']}{item['mes']:02d}"): {
                    "u": item["qt_u"],
                    "cx": item["qt_cx"],
                    "cx9": item["qt_cx9"],
                }
                for item in raw_data
            }

        return data

    def get_forecast(self):
        return []

    def list(self, user_id):
        # Populate
        lista_familia = defaultdict(list)
        lista_teste = []
        result_json = {}

        raw_sale_history = self.get_history()
        raw_sale_forecast = self.get_forecast()
        raw_tendency = self.get_tendency()

        products = self.get_product(user_id)

        # Aggregate data
        sale_history = self.aggregate(products=products, target=raw_sale_history)
        sale_forecast = self.aggregate(products=products, target=raw_sale_forecast)
        tendency = self.aggregate(products=products, target=raw_tendency)

        for product_item in products:
            familia = product_item["familia"]

            product_key = self.get_product_key(
                family=product_item["familia"],
                article=product_item["artigo"],
                company=product_item["empresa"],
                bo=product_item["bo"],
            )

            product_item["history"] = sale_history[product_key]
            product_item["forecast"] = sale_forecast[product_key]
            product_item["tendency"] = tendency[product_key]

            lista_familia[familia].append(product_item)

        result_json = {}

        for familia, produtos in lista_familia.items():
            lista_teste = []
            for product_item in produtos:
                forecast = self.extract_sales_values(product_item["forecast"])
                history = self.extract_sales_values(product_item["history"])

                tendency = {}
                if product_item["tendency"]:
                    raw_tendency = product_item["tendency"][0]
                    tendency = {
                        "trimester_average": raw_tendency["media_trimestral"],
                        "trimester_tendency": raw_tendency["tendencia_trimestral"],
                        "anual_average": raw_tendency["media_anual"],
                        "anual_tendency": raw_tendency["tendencia_anual"],
                        "weighted_tendency": raw_tendency["tendencia_ponderada"],
                        "anual_base": raw_tendency["base_anual"],
                    }

                product_data = {
                    **self.product_base_data(product_item),
                    "tendency": tendency,
                    "history": history,
                    "forecast": forecast,
                }

                lista_teste.append(product_data)

            result_json[familia] = lista_teste

        return result_json
