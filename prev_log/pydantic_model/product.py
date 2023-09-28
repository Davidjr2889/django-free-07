from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ProductStatus(Enum):
    active = "M"
    inactive = "N"


class PyTendency(BaseModel):
    average_trimester: Optional[float] = None
    tendency_trimester: Optional[float] = None
    average_anual: Optional[float] = None
    tendency_anual: Optional[float] = None
    weighted_tendency: Optional[float] = None


class ProductIdentification(BaseModel):
    empresa: str
    bo: str
    familia: str
    artigo: str
