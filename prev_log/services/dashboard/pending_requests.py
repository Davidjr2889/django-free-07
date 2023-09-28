from typing import Any, Dict

from prev_log.exceptions import PrevLogBadRequestException
from prev_log.models import ForecastManualChangeLog
from prev_log.services.utils.log import LogForecastOrigin
from prev_log.services.utils.products import get_product_key


def get_single_request_from_data(data: Dict[str, Any], origin: LogForecastOrigin):
    processed_items = {}
    filtered_results = []

    results = sorted(
        data,
        key=lambda entry: entry["created_at"],
        reverse=True,
    )

    for log_item in results:
        prod_key = get_product_key(
            family=log_item["familia"],
            article=log_item["artigo"],
            company=log_item["empresa"],
            bo=log_item["bo"],
        )
        key = f"{prod_key}-{origin}"

        del log_item["qt_cx"]
        del log_item["qt_cx9"]

        # Corresponding log
        log = ForecastManualChangeLog.objects.filter(id=log_item["log_id"]).first()
        if not log:
            raise PrevLogBadRequestException(
                error="dashboard pending requests",
                details="processing requesting without log",
            )

        del log_item["log_id"]
        if not processed_items.get(key):
            filtered_results.append(
                {
                    **log_item,
                    "prev_qt_u": log.prev_qt_u,
                    "origin": origin.value,
                }
            )
            processed_items[key] = True

    return filtered_results
