from datetime import datetime, timezone
from typing import cast

from backoffice.models import UserDataPerm
from prev_log.exceptions import PrevLogBadRequestException
from prev_log.models import (
    ForecastManualChangeLog,
    OrigemPrevisao,
    Product,
    StockForecast,
    StockForecastOpenRequest,
)
from prev_log.pydantic_model.product import ProductIdentification
from prev_log.pydantic_model.stock import ChangeRequestParams, ConfirmRequestParams
from prev_log.services.utils.log import LogForecastOrigin, ManualChangeStatus


def make_stock_change_request(params: ChangeRequestParams):
    filters = ProductIdentification(**params.dict())
    creation_date = datetime.now(tz=timezone.utc)

    # Make sure the product exists
    prod_query = Product.objects.filter(**filters.dict())
    products = UserDataPerm.get_safe_qs(prod_query, params.utilizador_id).all()

    if len(products) != 1:
        raise PrevLogBadRequestException(
            error="stock change request",
            details="invalid product",
        )

    # Initialize previous values
    previous_qty = {
        "prev_qt_u": 0,
        "prev_qt_cx": 0,
        "prev_qt_cx9": 0,
    }

    # Get current forecast if exists
    current_forecast = StockForecast.objects.filter(
        **filters.dict(),
        ano=params.ano,
        mes=params.mes,
    ).first()
    if current_forecast:
        previous_qty = {
            "prev_qt_u": current_forecast.qt_u,
            "prev_qt_cx": current_forecast.qt_cx,
            "prev_qt_cx9": current_forecast.qt_cx9,
        }

    # Log the request
    log = ForecastManualChangeLog.objects.create(
        **params.dict(),
        **previous_qty,
        created_at=creation_date,
        origem_forecast=LogForecastOrigin.STOCK.value,
        status=ManualChangeStatus.REQUESTED.value,
    )

    # Publish request to table
    StockForecastOpenRequest.objects.create(
        **params.dict(),
        created_at=creation_date,
        log=log,
    )


def confirm_stock_change_request(params: ConfirmRequestParams):
    # check for associted request
    original_request = StockForecastOpenRequest.objects.filter(
        id=params.request_id
    ).first()
    if not original_request:
        raise PrevLogBadRequestException(
            error="stock confirm request",
            details="invalid request",
        )

    filters = ProductIdentification.parse_obj(params.dict())
    curr_date = datetime.now(tz=timezone.utc)
    parent_log = cast(ForecastManualChangeLog, original_request.log)

    # Log the decision
    ForecastManualChangeLog.objects.create(
        **filters.dict(),
        comentario=params.comentario,
        utilizador_id=params.utilizador_id,
        utilizador=params.utilizador,
        parent_request=parent_log,
        created_at=curr_date,
        origem_forecast=LogForecastOrigin.STOCK.value,
        status=params.status,
        ano=parent_log.ano,
        mes=parent_log.mes,
        qt_u=parent_log.qt_u,
        qt_cx=parent_log.qt_cx,
        qt_cx9=parent_log.qt_cx9,
        prev_qt_u=parent_log.prev_qt_u,
        prev_qt_cx=parent_log.prev_qt_cx9,
        prev_qt_cx9=parent_log.prev_qt_cx9,
    )

    # let's process the rejection first
    if params.status == ManualChangeStatus.DECLINED.value:
        # Delete the open request without making further changes
        original_request.delete()
        return

    # let's process the aproval first
    if params.status == ManualChangeStatus.APPROVED.value:
        origem = OrigemPrevisao.objects.filter(designacao=OrigemPrevisao.MANUAL).first()

        # Update the forecast
        [forecast, _] = StockForecast.objects.get_or_create(
            **filters.dict(),
            ano=original_request.ano,
            mes=original_request.mes,
            defaults={"origem": origem},
        )
        forecast = cast(StockForecast, forecast)

        forecast.origem = origem
        forecast.qt_u = original_request.qt_u
        forecast.qt_cx = original_request.qt_cx
        forecast.qt_cx9 = original_request.qt_cx9

        forecast.save()

        # Delete all the associated open requests
        # to the forecast of this product and year/month combination
        StockForecastOpenRequest.objects.filter(
            **filters.dict(),
            ano=original_request.ano,
            mes=original_request.mes,
        ).delete()

        return

    raise PrevLogBadRequestException(
        error="stock confirm request",
        details="invalid status",
    )
