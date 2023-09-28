from prev_log.pydantic_model.user import UserIdentification
from prev_log.services.utils.log import ManualChangeStatus

from .product import ProductIdentification


class ChangeRequestParams(ProductIdentification, UserIdentification):
    comentario: str

    ano: float
    mes: float

    qt_u: float
    qt_cx: float
    qt_cx9: float


class ConfirmRequestParams(
    ProductIdentification,
    UserIdentification,
    use_enum_values=True,
):
    comentario: str

    request_id: int
    status: ManualChangeStatus
