from django.conf.urls import include, url
from rest_framework import routers

from . import views as prev_log_views

router = routers.SimpleRouter()

urlpatterns = [
    url(
        "dashboard/stock/",
        prev_log_views.DashboardPageStockDataView.as_view(),
        name="get_dashboard_stock_data",
    ),
    url(
        "dashboard/pending/",
        prev_log_views.DashboardPagePendingDataView.as_view(),
        name="get_dashboard_pending_data",
    ),
    url(
        "dashboard/sale/",
        prev_log_views.DashboardPageDeviationDataView.as_view(),
        name="get_dashboard_sale_data",
    ),
    url(
        "dashboard/forecast/",
        prev_log_views.DashboardPageProductsWithoutForecastDataView.as_view(),
        name="get_dashboard_product_without_forecast",
    ),
    url(
        "stocks/",
        prev_log_views.StockPageBaseDataView.as_view(),
        name="get_stock_data",
    ),
    url(
        "stock/change/",
        prev_log_views.StockPageUpdateForecastDataView.as_view(),
        name="change_stock_data",
    ),
    url(
        "sales/",
        prev_log_views.SalesPageBaseDataView.as_view(),
        name="list_product_sales_data",
    ),
    url(
        "sale/change/",
        prev_log_views.SalesPageUpdateForecastDataView.as_view(),
        name="list_product_sales_data",
    ),
    url(
        "sale/tendency/change/",
        prev_log_views.SalesPageUpdateTendencyDataView.as_view(),
        name="update_anual_base_data",
    ),
    url(
        "purchases/",
        prev_log_views.PurchasePageBaseDataView.as_view(),
        name="purchase_list_data",
    ),
    url(
        "logs/",
        prev_log_views.LogEvents.as_view(),
        name="logs_list_data",
    ),
    url(
        "purchase/change",
        prev_log_views.PurchasePageUpdateForecastDataView.as_view(),
        name="change_purchase_data",
    ),
    url(
        "orders/",
        prev_log_views.OrdersPageBaseDataView.as_view(),
        name="product_orders_data",
    ),
    url(r"^", include(router.urls)),
]
