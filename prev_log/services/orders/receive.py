from datetime import datetime, timezone

from prev_log.models import ApprovedOrderRequests
from prev_log.pydantic_model.order import MultipleOrderCreatePayload
from prev_log.pydantic_model.user import UserIdentification


def create_approved_orders(
    user_identification: UserIdentification,
    order_list: MultipleOrderCreatePayload,
):
    created_at = datetime.now(tz=timezone.utc)

    for order_item in order_list.orders:
        ApprovedOrderRequests.objects.create(
            created_at=created_at,
            **user_identification.dict(),
            **order_item.dict(),
        )
