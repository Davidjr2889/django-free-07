from datetime import datetime, timezone

from prev_log.models import (
    ForecastManualChangeLog,
    Tendency,
)
from prev_log.pydantic_model.product import ProductIdentification
from prev_log.pydantic_model.sale import TendencyChangeRequestParams
from prev_log.services.utils.log import LogForecastOrigin, ManualChangeStatus


def update_anual_base_tendency(params: TendencyChangeRequestParams):
    filters = ProductIdentification(**params.dict())
    creation_date = datetime.now(tz=timezone.utc)

    [tendency, _] = Tendency.objects.get_or_create(
        **filters.dict(), defaults={"base_anual": 0}
    )

    ForecastManualChangeLog.objects.create(
        **filters.dict(),
        utilizador_id=params.utilizador_id,
        utilizador=params.utilizador,
        comentario=params.comentario,
        created_at=creation_date,
        qt_u=params.base_anual,
        qt_cx=params.base_anual,
        qt_cx9=params.base_anual,
        ano=creation_date.year,
        mes=creation_date.month,
        prev_qt_u=tendency.base_anual,
        prev_qt_cx=tendency.base_anual,
        prev_qt_cx9=tendency.base_anual,
        origem_forecast=LogForecastOrigin.TENDENCY.value,
        status=ManualChangeStatus.APPROVED.value,
    )

    tendency.base_anual = params.base_anual
    tendency.save()
