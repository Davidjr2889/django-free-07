import json
from collections import defaultdict

from django.db.models import F, Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View

from backoffice.models import UserDataPerm
from jwt_auth.mixins import JSONWebTokenAuthMixin
from prev_log.exceptions import PrevLogBadRequestException
from prev_log.models import (
    ForecastManualChangeLog,
    Product,
    PurchaseForecastOpenRequest,
    Sale,
    SaleForecast,
    SaleForecastOpenRequest,
    StockForecastOpenRequest,
)
from prev_log.pydantic_model.order import MultipleOrderCreatePayload
from prev_log.pydantic_model.product import ProductIdentification
from prev_log.pydantic_model.sale import TendencyChangeRequestParams
from prev_log.pydantic_model.stock import ChangeRequestParams, ConfirmRequestParams
from prev_log.pydantic_model.user import UserIdentification
from prev_log.services.dashboard.list import ProductsNotDataViewSet
from prev_log.services.dashboard.pending_requests import get_single_request_from_data
from prev_log.services.orders.list import list_orders
from prev_log.services.orders.receive import create_approved_orders
from prev_log.services.purchase.change import (
    confirm_purchase_change_request,
    make_purchase_change_request,
)
from prev_log.services.purchase.list import PurchaseViewSet
from prev_log.services.sales.change import (
    confirm_sale_change_request,
    make_sale_forecast_change_request,
)
from prev_log.services.sales.list import SaleViewSet
from prev_log.services.sales.update import update_anual_base_tendency
from prev_log.services.sales.utils.forecast import (
    simulate_updated_sales_forecast,
    translated_sale_forecast_simulation,
)
from prev_log.services.stock.change import (
    confirm_stock_change_request,
    make_stock_change_request,
)
from prev_log.services.stock.list import StockListing
from prev_log.services.utils.filters import filter_two_years_ago
from prev_log.services.utils.log import LogForecastOrigin
from prev_log.services.utils.products import (
    aggreagate_by_product,
    get_all_products,
    get_product_key,
    product_base_data,
)
from prev_log.tasks import task_update_single_product_forecasts


class LogEvents(JSONWebTokenAuthMixin, View):
    http_method_names = ["get"]

    def get(self, request):
        # possible filters:
        origem_forecast = request.GET.get("origem", None)
        status = request.GET.get("status", None)
        showAll = request.GET.get("showAll", "false") == "true"

        data = ForecastManualChangeLog.objects
        if origem_forecast:
            data = data.filter(origem_forecast=origem_forecast)

        if status:
            data = data.filter(status=status)

        results = UserDataPerm.get_safe_qs(
            data.order_by("-created_at"),
            request.user.id,
        ).values()
        # show all events for everything
        if showAll:
            return JsonResponse({"events": results})

        # For each module show only the latest event
        filtered_results = []
        processed_items = {}
        for log_item in results:
            prod_key = get_product_key(
                family=log_item["familia"],
                article=log_item["artigo"],
                company=log_item["empresa"],
                bo=log_item["bo"],
            )
            key = f'{prod_key}-{log_item["origem_forecast"]}'
            if not processed_items.get(key):
                log_item["created_at"] = log_item["created_at"].strftime(
                    "%d/%m/%Y as %H:%M"
                )
                filtered_results.append(log_item)
                processed_items[key] = True

        return JsonResponse({"events": filtered_results})


class DashboardPageStockDataView(JSONWebTokenAuthMixin, View):
    http_method_names = ["get"]

    def get(self, request):
        # Produtos com estoque crítico:
        prod_query = Product.objects.filter(
            Q(stock_actual__lt=F("stock_minimo")) | Q(stock_actual=0)
        )
        products = UserDataPerm.get_safe_qs(prod_query, request.user.id).all()

        results = products.values()

        # CHeck if we should group by family
        grouping = request.GET.get("group_by", None)
        if grouping and grouping == "family":
            grouped_results = defaultdict(list)

            for product_item in results:
                grouped_results[product_item["familia"]] = product_item

            return JsonResponse({"products": grouped_results})

        return JsonResponse({"products": list(results)})


class DashboardPageDeviationDataView(JSONWebTokenAuthMixin, View):
    http_method_names = ["get"]

    def get(self, request):
        response = []

        # Get products
        products = get_all_products(request.user.id)

        # Sale History
        history_tuples = Sale.objects.filter(filter_two_years_ago()).values()
        history = aggreagate_by_product(
            products=products,
            target=history_tuples,
        )

        # Sale Forecast (we just want from past 12 months)
        forecast_tuples = SaleForecast.objects.filter(filter_two_years_ago()).values()
        forecast = aggreagate_by_product(
            products=products,
            target=forecast_tuples,
        )

        for product_item in products:
            key = get_product_key(
                family=product_item["familia"],
                article=product_item["artigo"],
                company=product_item["empresa"],
                bo=product_item["bo"],
            )
            item = product_base_data(product=product_item)
            item["history"] = history[key]
            item["forecast"] = forecast[key]

            response.append(item)

        return JsonResponse({"products": response})


class DashboardPageProductsWithoutForecastDataView(JSONWebTokenAuthMixin, View):
    http_method_name = ["get"]

    def get(self, request):
        results = ProductsNotDataViewSet().list(request.user.id)
        return JsonResponse({"products": results})


class DashboardPagePendingDataView(JSONWebTokenAuthMixin, View):
    http_method_names = ["get"]

    def get(self, request):
        response = []

        # Stock Change requests
        stock_raw_data = UserDataPerm.get_safe_qs(
            StockForecastOpenRequest.objects,
            request.user.id,
        ).values()
        response.extend(
            get_single_request_from_data(
                data=stock_raw_data,
                origin=LogForecastOrigin.STOCK,
            )
        )

        # Purchase change requests
        purchase_raw_data = UserDataPerm.get_safe_qs(
            PurchaseForecastOpenRequest.objects,
            request.user.id,
        ).values()
        response.extend(
            get_single_request_from_data(
                data=purchase_raw_data,
                origin=LogForecastOrigin.PURCHASE,
            )
        )

        # Sales change requests
        sale_raw_data = UserDataPerm.get_safe_qs(
            SaleForecastOpenRequest.objects,
            request.user.id,
        ).values()
        response.extend(
            get_single_request_from_data(
                data=sale_raw_data,
                origin=LogForecastOrigin.PURCHASE,
            )
        )

        return JsonResponse({"requests": response})


class StockPageBaseDataView(JSONWebTokenAuthMixin, View):
    http_method_names = ["get"]

    def get(self, request):
        results = StockListing().list(request.user.id)

        return JsonResponse({"products": results})


class StockPageUpdateForecastDataView(JSONWebTokenAuthMixin, View):
    http_method_names = ["put", "post"]

    def post(self, request: HttpRequest):
        try:
            body = json.loads(request.body)
            change_params = ConfirmRequestParams(
                empresa=body["company"],
                bo=body["bo"],
                familia=body["family"],
                artigo=body["article"],
                utilizador=request.user.get_username(),
                utilizador_id=request.user.id,
                comentario=body["description"],
                request_id=body["request_id"],
                status=body["decision"],
            )

            confirm_stock_change_request(params=change_params)
            return HttpResponse(status=202)

        except PrevLogBadRequestException as exc:
            return exc.http_return()

    def put(self, request: HttpRequest):
        try:
            body = json.loads(request.body)
            change_params = ChangeRequestParams(
                empresa=body["company"],
                bo=body["bo"],
                familia=body["family"],
                artigo=body["article"],
                utilizador=request.user.get_username(),
                utilizador_id=request.user.id,
                comentario=body["description"],
                ano=body["year"],
                mes=body["month"],
                qt_u=body["qt_u"],
                qt_cx=body["qt_cx"],
                qt_cx9=body["qt_cx9"],
            )

            make_stock_change_request(params=change_params)
            return HttpResponse(status=202)

        except PrevLogBadRequestException as exc:
            return exc.http_return()


class SalesPageBaseDataView(JSONWebTokenAuthMixin, View):
    http_method_names = ["get"]

    def get(self, request):
        results = SaleViewSet().list(request.user.id)

        return JsonResponse({"products": results})


class SalesPageUpdateTendencyDataView(JSONWebTokenAuthMixin, View):
    http_method_names = ["get", "post"]

    def get(self, request):
        # possible filters:
        try:
            base_anual = float(request.GET.get("base_anual", "0"))
            empresa = request.GET.get("empresa", "")
            bo = request.GET.get("bo", "")
            familia = request.GET.get("familia", "")
            artigo = request.GET.get("artigo", "")

            product_filter = ProductIdentification(
                empresa=empresa,
                bo=bo,
                familia=familia,
                artigo=artigo,
            )

            # Return a simulated response
            simulated = simulate_updated_sales_forecast(
                filters=product_filter,
                base_anual=base_anual,
            )
            response = translated_sale_forecast_simulation(forecasted=simulated)

            return JsonResponse(
                data={"simulation": response},
                status=200,
            )

        except PrevLogBadRequestException as exc:
            return exc.http_return()

    def post(self, request):
        try:
            body = json.loads(request.body)
            change_params = TendencyChangeRequestParams(
                empresa=body["company"],
                bo=body["bo"],
                familia=body["family"],
                artigo=body["article"],
                utilizador=request.user.get_username(),
                utilizador_id=request.user.id,
                comentario=body["description"],
                base_anual=body["base_anual"],
            )
            product_filter = ProductIdentification.parse_obj(
                change_params.dict(),
            )

            update_anual_base_tendency(params=change_params)

            # Start celery task to update all the forecast in the background
            task_update_single_product_forecasts.apply_async(
                args=[
                    product_filter.empresa,
                    product_filter.bo,
                    product_filter.familia,
                    product_filter.artigo,
                ],
            )

            # Return a simulated response
            simulated = simulate_updated_sales_forecast(
                filters=product_filter,
                base_anual=change_params.base_anual,
            )
            response = translated_sale_forecast_simulation(forecasted=simulated)

            return JsonResponse(
                data={"simulation": response},
                status=200,
            )

        except PrevLogBadRequestException as exc:
            return exc.http_return()


class SalesPageUpdateForecastDataView(JSONWebTokenAuthMixin, View):
    http_method_names = ["put", "post"]

    def post(self, request: HttpRequest):
        try:
            body = json.loads(request.body)
            change_params = ConfirmRequestParams(
                empresa=body["company"],
                bo=body["bo"],
                familia=body["family"],
                artigo=body["article"],
                utilizador=request.user.get_username(),
                utilizador_id=request.user.id,
                comentario=body["description"],
                request_id=body["request_id"],
                status=body["decision"],
            )

            confirm_sale_change_request(params=change_params)
            return HttpResponse(status=202)

        except PrevLogBadRequestException as exc:
            return exc.http_return()

    def put(self, request: HttpRequest):
        try:
            body = json.loads(request.body)
            change_params = ChangeRequestParams(
                empresa=body["company"],
                bo=body["bo"],
                familia=body["family"],
                artigo=body["article"],
                utilizador=request.user.get_username(),
                utilizador_id=request.user.id,
                comentario=body["description"],
                ano=body["year"],
                mes=body["month"],
                qt_u=body["qt_u"],
                qt_cx=body["qt_cx"],
                qt_cx9=body["qt_cx9"],
            )

            make_sale_forecast_change_request(params=change_params)
            return HttpResponse(status=202)

        except PrevLogBadRequestException as exc:
            return exc.http_return()


class PurchasePageBaseDataView(JSONWebTokenAuthMixin, View):
    http_method_names = ["get"]

    def get(self, request):
        results = PurchaseViewSet().list(request.user.id)

        return JsonResponse({"products": results})


class PurchasePageUpdateForecastDataView(JSONWebTokenAuthMixin, View):
    http_method_names = ["put", "post"]

    def post(self, request: HttpRequest):
        try:
            body = json.loads(request.body)
            change_params = ConfirmRequestParams(
                empresa=body["company"],
                bo=body["bo"],
                familia=body["family"],
                artigo=body["article"],
                utilizador=request.user.get_username(),
                utilizador_id=request.user.id,
                comentario=body["description"],
                request_id=body["request_id"],
                status=body["decision"],
            )

            confirm_purchase_change_request(params=change_params)
            return HttpResponse(status=202)

        except PrevLogBadRequestException as exc:
            return exc.http_return()

    def put(self, request: HttpRequest):
        try:
            body = json.loads(request.body)
            change_params = ChangeRequestParams(
                empresa=body["company"],
                bo=body["bo"],
                familia=body["family"],
                artigo=body["article"],
                utilizador=request.user.get_username(),
                utilizador_id=request.user.id,
                comentario=body["description"],
                ano=body["year"],
                mes=body["month"],
                qt_u=body["qt_u"],
                qt_cx=body["qt_cx"],
                qt_cx9=body["qt_cx9"],
            )

            make_purchase_change_request(params=change_params)
            return HttpResponse(status=202)

        except PrevLogBadRequestException as exc:
            return exc.http_return()


class OrdersPageBaseDataView(JSONWebTokenAuthMixin, View):
    http_method_names = ["get", "put"]

    def get(self, request):
        results = list_orders(request.user.id)

        return JsonResponse({"products": results})

    def put(self, request: HttpRequest):
        try:
            body = json.loads(request.body)

            user_identification = UserIdentification(
                utilizador=request.user.get_username(),
                utilizador_id=request.user.id,
            )

            order_list = MultipleOrderCreatePayload(orders=body["order_list"])

            create_approved_orders(
                user_identification=user_identification,
                order_list=order_list,
            )
            return HttpResponse(status=204)

        except PrevLogBadRequestException as exc:
            return exc.http_return()
