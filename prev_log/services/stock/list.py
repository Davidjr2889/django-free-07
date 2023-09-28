from collections import defaultdict

from prev_log.models import Stock, StockForecast
from prev_log.services.stock.utils.aggregate import merge_stock_data
from prev_log.services.utils.products import BaseProductListing


class StockListing(BaseProductListing):
    def get_stock(self):
        return Stock.objects.values()

    def get_stock_forecast(self):
        return StockForecast.objects.values()

    def list(self, user_id):
        # Populate
        lista_familia = defaultdict(list)

        # Fetch Data
        products = self.get_product(user_id)
        stock_data = self.get_stock()
        stock_forecast_data = self.get_stock_forecast()

        # Aggregated Stock
        history_product = self.aggregate(
            products=products,
            target=stock_data,
        )
        forecast_product = self.aggregate(
            products=products,
            target=stock_forecast_data,
        )

        # Generate list of families in the stock
        for product_item in products:
            familia = product_item["familia"]

            product_key = self.get_product_key(
                family=product_item["familia"],
                article=product_item["artigo"],
                company=product_item["empresa"],
                bo=product_item["bo"],
            )

            base_data = self.product_base_data(product_item)
            product_stock_history = history_product[product_key]
            product_stock_forecast = forecast_product[product_key]

            forecast = {}
            if product_stock_forecast:
                forecast = {
                    (f"{item['ano']}{item['mes']:02d}"): {
                        "u": item["qt_u"],
                        "cx": item["qt_cx"],
                        "cx9": item["qt_cx9"],
                    }
                    for item in product_stock_forecast
                }

            product_data = {
                **base_data,
                "history": merge_stock_data(product_stock_history),
                "forecast": forecast,
            }

            lista_familia[familia].append(product_data)

        return lista_familia
