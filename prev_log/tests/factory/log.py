from datetime import datetime, timezone
from random import randint

import factory

from prev_log.models import ForecastManualChangeLog
from prev_log.services.utils.log import ManualChangeStatus


class ForecastManualChangeLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ForecastManualChangeLog

    ano = randint(2000, 3000)
    mes = randint(1, 12)
    status = ManualChangeStatus.REQUESTED.value
    created_at = datetime.now(tz=timezone.utc)
    utilizador_id = randint(0, 1000000)
    qt_u = randint(100, 500)
    qt_cx = randint(100, 500)
    qt_cx9 = randint(100, 500)
    prev_qt_u = randint(100, 500)
    prev_qt_cx = randint(100, 500)
    prev_qt_cx9 = randint(100, 500)
