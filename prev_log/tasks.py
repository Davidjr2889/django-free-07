import time
from contextlib import contextmanager

from celery.utils.log import get_task_logger
from django.core.cache import cache
from django.utils import timezone

from LBARM.celery import app
from prev_log.models import Product
from prev_log.services.task import update_product_forecast

logger = get_task_logger(__name__)

LOCK_EXPIRE = 60 * 30
TASK_GROUP_ID = "recalc_metrics-LOCK"


@app.task(
    name="recalc_metrics_ptask",
    bind=True,
    task_retries=5,
    ignore_result=False,
    track_started=True,
    default_retry_delay=60,
)
def recalc_metrics_ptask(self, extra_params=None):
    def acquire_lock():
        return cache.add(TASK_GROUP_ID, "true", LOCK_EXPIRE)

    def release_lock():
        cache.delete(TASK_GROUP_ID)

    t0 = time.clock()
    if acquire_lock():
        try:
            pass

            t1 = time.clock()
            logger.info(
                "recalc_metrics_ptask (%s): %s segs"
                % (timezone.now().strftime("%Y-%m-%d %H:%M"), t1 - t0)
            )
        except Exception as exc:
            raise self.retry(exc=exc)
        finally:
            release_lock()


@contextmanager
def memcache_lock(lock_id, oid):
    """
    Source: https://docs.celeryq.dev/en/stable/tutorials/task-cookbook.html
    Access date: 2023-08-26
    """

    timeout_at = time.monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if time.monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)


@app.task(
    name="update_all_products_forecast",
    bind=True,
)
def task_update_all_forecasts(self):
    lock_id = f"{self.name}-lock-{TASK_GROUP_ID}"

    with memcache_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            # Get all products
            products = Product.objects.all()

            for product_item in products:
                update_product_forecast(product=product_item)


@app.task(
    name="update_single_products_forecast",
    bind=True,
)
def task_update_single_product_forecasts(self, empresa, bo, familia, artigo):
    lock_id = f"{self.name}-lock-{TASK_GROUP_ID}"

    with memcache_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            product = Product.objects.filter(
                empresa=empresa,
                bo=bo,
                familia=familia,
                artigo=artigo,
            ).first()

            update_product_forecast(product=product)
