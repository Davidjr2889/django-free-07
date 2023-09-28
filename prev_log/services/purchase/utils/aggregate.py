from typing import Any, Dict, List


def merge_purchase_data(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    result = {}

    for item in history:
        result[f"{item['ano']}{item['mes']:02d}"] = {
            "u": float(item["qt_u"]),
            "cx": float(item["qt_cx"]),
            "cx9": float(item["qt_cx9"]),
        }

    return result
