from datetime import datetime, timezone
from typing import Dict

from pydantic import BaseModel


class EntryQty(BaseModel):
    u: int = 0
    cx: int = 0
    cx9: int = 0


class QtyRatios(BaseModel):
    cx: float = 1
    cx9: float = 1

    @classmethod
    def from_entry(cls, entry: Dict[str, Dict[int, float]]):
        target_key = list(entry["u"].keys())[0]

        normalizer = entry["u"][target_key] or 1
        base_cx = entry["cx"][target_key] or 1
        base_cx9 = entry["cx9"][target_key] or 1

        return cls(
            cx=(base_cx / normalizer),
            cx9=(base_cx9 / normalizer),
        )


class PurchaseEntryQty(EntryQty):
    order_date: datetime = datetime.now(tz=timezone.utc)
