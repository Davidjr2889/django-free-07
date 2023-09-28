from datetime import datetime, timezone
from typing import cast

from backoffice.models import UserDataPerm
from prev_log.exceptions import PrevLogBadRequestException
from prev_log.models import (
    ForecastManualChangeLog,
    OrigemPrevisao,
    Product,
    SaleForecast,
    SaleForecastOpenRequest,
)
from prev_log.pydantic_model.product import ProductIdentification
from prev_log.pydantic_model.stock import ChangeRequestParams, ConfirmRequestParams
from prev_log.services.utils.log import LogForecastOrigin, ManualChangeStatus


def make_sale_forecast_change_request(params: ChangeRequestParams):
    filters = ProductIdentification(**params.dict())
    creation_date = datetime.now(tz=timezone.utc)

    prod_query = Product.objects.filter(**filters.dict())
    product = UserDataPerm.get_safe_qs(prod_query, params.utilizador_id).all()

    if len(product) != 1:
        raise PrevLogBadRequestException(
            error="sale change request",
            details="invalid product",
        )

    previous_qty = {
        "prev_qt_u": 0,
        "prev_qt_cx": 0,
        "prev_qt_cx9": 0,
    }

    current_saleforecast = SaleForecast.objects.filter(
        **filters.dict(), ano=params.ano, mes=params.mes
    ).first()
    if current_saleforecast:
        previous_qty = {
            "prev_qt_u": current_saleforecast.qt_u,
            "prev_qt_cx": current_saleforecast.qt_cx,
            "prev_qt_cx9": current_saleforecast.qt_cx9,
        }

    log = ForecastManualChangeLog.objects.create(
        **filters.dict(),
        **previous_qty,
        created_at=creation_date,
        utilizador_id=params.utilizador_id,
        utilizador=params.utilizador,
        comentario=params.comentario,
        mes=params.mes,
        ano=params.ano,
        qt_u=params.qt_u,
        qt_cx=params.qt_cx,
        qt_cx9=params.qt_cx9,
        origem_forecast=LogForecastOrigin.SALES.value,
        status=ManualChangeStatus.REQUESTED.value,
    )

    SaleForecastOpenRequest.objects.create(
        **params.dict(),
        created_at=creation_date,
        log=log,
    )


def confirm_sale_change_request(params: ConfirmRequestParams):
    original_request = SaleForecastOpenRequest.objects.filter(
        id=params.request_id
    ).first()
    if not original_request:
        raise PrevLogBadRequestException(
            error="sale confirm request",
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
        origem_forecast=LogForecastOrigin.SALES.value,
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

        [forecast, _] = SaleForecast.objects.get_or_create(
            **filters.dict(),
            ano=original_request.ano,
            mes=original_request.mes,
            defaults={"origem": origem},
        )

        forecast = cast(SaleForecast, forecast)

        forecast.origem = origem
        forecast.qt_u = original_request.qt_u
        forecast.qt_cx = original_request.qt_cx
        forecast.qt_cx9 = original_request.qt_cx9

        forecast.save()

        SaleForecastOpenRequest.objects.filter(
            **filters.dict(),
            ano=original_request.ano,
            mes=original_request.mes,
        ).delete()
        return

    raise PrevLogBadRequestException(
        error="sale confirm request", details="invalid status"
    )
