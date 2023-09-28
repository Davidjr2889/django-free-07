from typing import Any, Dict, List

from prev_log.services.utils.indexes import generate_index


def merge_stock_data(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    result = {}

    for item in history:
        # yyyymmdd as integer
        int_day = int(item["dia"].strftime("%Y%m%d"))

        # 'yyyymm'  for the index
        index = generate_index(target_date=item["dia"])

        # Merge when needed
        values = result.get(index, None)
        if not values:
            result[index] = {
                "last_day": int_day,
                "u": float(item["stock_u"]),
                "cx": float(item["stock_cx"]),
                "cx9": float(item["stock_cx9"]),
            }
            continue

        # We just want the lastest day from the range
        if result[index]["last_day"] < int_day:
            result[index] = {
                "last_day": int_day,
                "u": float(item["stock_u"]),
                "cx": float(item["stock_cx"]),
                "cx9": float(item["stock_cx9"]),
            }
            continue

        # For the same day, we want to join the warehouses
        if result[index]["last_day"] == int_day:
            result[index]["u"] += float(item["stock_u"])
            result[index]["cx"] += float(item["stock_cx"])
            result[index]["cx9"] += float(item["stock_cx9"])

    return result
