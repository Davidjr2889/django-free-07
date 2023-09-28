from prev_log.pydantic_model.user import UserIdentification

from .product import ProductIdentification


class TendencyChangeRequestParams(ProductIdentification, UserIdentification):
    comentario: str
    base_anual: float
