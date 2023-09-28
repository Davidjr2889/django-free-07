from datetime import datetime, timezone
from typing import cast

from backoffice.models import UserDataPerm
from prev_log.exceptions import PrevLogBadRequestException
from prev_log.models import (
    ForecastManualChangeLog,
    OrigemPrevisao,
    Product,
    PurchaseForecast,
    PurchaseForecastOpenRequest,
)
from prev_log.pydantic_model.product import ProductIdentification
from prev_log.pydantic_model.stock import ChangeRequestParams, ConfirmRequestParams
from prev_log.services.utils.log import LogForecastOrigin, ManualChangeStatus


def make_purchase_change_request(params: ChangeRequestParams):
    filters = ProductIdentification(**params.dict())

    # Make sure the product exists
    prod_query = Product.objects.filter(**filters.dict())
    products = UserDataPerm.get_safe_qs(prod_query, params.utilizador_id).all()

    if not products.exists():
        raise PrevLogBadRequestException(
            error="stock change request",
            details="invalid product",
        )

    # # Initialize previous values
    previous_qty = {
        "prev_qt_u": 0,
        "prev_qt_cx": 0,
        "prev_qt_cx9": 0,
    }

    current_forecast = PurchaseForecast.objects.filter(
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

    log = ForecastManualChangeLog.objects.create(
        **filters.dict(),
        **previous_qty,
        created_at=datetime.now(tz=timezone.utc),
        utilizador_id=params.utilizador_id,
        utilizador=params.utilizador,
        comentario=params.comentario,
        mes=params.mes,
        ano=params.ano,
        qt_u=params.qt_u,
        qt_cx=params.qt_cx,
        qt_cx9=params.qt_cx9,
        origem_forecast=LogForecastOrigin.PURCHASE.value,
        status=ManualChangeStatus.REQUESTED.value,
    )

    # Publish request to table
    PurchaseForecastOpenRequest.objects.create(
        **params.dict(),
        created_at=datetime.now(tz=timezone.utc),
        log=log,
    )


def confirm_purchase_change_request(params: ConfirmRequestParams):
    original_request = PurchaseForecastOpenRequest.objects.filter(
        id=params.request_id
    ).first()
    if not original_request:
        raise PrevLogBadRequestException(
            error="purchase confirm request",
            details="invalid request",
        )

    filters = ProductIdentification.parse_obj(params.dict())
    curr_date = datetime.now(tz=timezone.utc)
    parent_log = cast(ForecastManualChangeLog, original_request.log)

    ForecastManualChangeLog.objects.create(
        **filters.dict(),
        comentario=params.comentario,
        utilizador_id=params.utilizador_id,
        utilizador=params.utilizador,
        parent_request=parent_log,
        created_at=curr_date,
        origem_forecast=LogForecastOrigin.PURCHASE.value,
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

    if params.status == ManualChangeStatus.DECLINED.value:
        original_request.delete()
        return

    if params.status == ManualChangeStatus.APPROVED.value:
        origem = OrigemPrevisao.objects.filter(designacao=OrigemPrevisao.MANUAL).first()

        [purcharse_forecast, _] = PurchaseForecast.objects.get_or_create(
            **filters.dict(),
            ano=original_request.ano,
            mes=original_request.mes,
        )

        purcharse_forecast = cast(PurchaseForecast, purcharse_forecast)

        purcharse_forecast.origem = origem
        purcharse_forecast.qt_u = original_request.qt_u
        purcharse_forecast.qt_cx = original_request.qt_cx
        purcharse_forecast.qt_cx9 = original_request.qt_cx9

        purcharse_forecast.save()

        PurchaseForecastOpenRequest.objects.filter(
            **filters.dict(),
            ano=original_request.ano,
            mes=original_request.mes,
        ).delete()
        return

    raise PrevLogBadRequestException(
        error="purchase confirm request", details="invalid status"
    )
