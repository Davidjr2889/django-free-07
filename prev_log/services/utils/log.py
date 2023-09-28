from enum import Enum


class LogForecastOrigin(Enum):
    STOCK = "stock"
    SALES = "sales"
    TENDENCY = "tendency"
    PURCHASE = "purchase"


class ManualChangeStatus(Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    DECLINED = "declined"
