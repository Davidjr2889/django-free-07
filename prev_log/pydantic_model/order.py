from datetime import date
from typing import List

from pydantic import BaseModel

from prev_log.pydantic_model.product import ProductIdentification


class OrderCreatePayload(ProductIdentification):
    data_do_pedido: date
    qt_u: float
    qt_cx: float
    qt_cx9: float


class MultipleOrderCreatePayload(BaseModel):
    orders: List[OrderCreatePayload]
