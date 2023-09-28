from datetime import date

from dateutil.relativedelta import relativedelta
from django.db.models import Q


def filter_future():
    curr_date = date.today()
    next_year = curr_date + relativedelta(years=1)
    return Q(
        ano__gte=next_year.year,
    ) | Q(
        ano=curr_date.year,
        mes__gte=curr_date.month,
    )


def filter_past():
    curr_date = date.today()
    one_years_ago = curr_date + relativedelta(years=-1)
    return Q(
        ano__lte=one_years_ago.year,
    ) | Q(
        ano=curr_date.year,
        mes__lt=curr_date.month,
    )


def filter_two_years_ago():
    curr_date = date.today()
    two_years_ago = curr_date + relativedelta(years=-2)
    return Q(
        ano__gte=two_years_ago.year,
        ano__lt=curr_date.year,
    ) | Q(
        ano=curr_date.year,
        mes__lte=curr_date.month,
    )


def filter_over_two_years_in_past():
    curr_date = date.today()
    two_years_ago = curr_date + relativedelta(years=-2)
    three_years_ago = curr_date + relativedelta(years=-3)
    return Q(
        ano__lte=three_years_ago.year,
    ) | Q(
        ano=two_years_ago.year,
        mes__lt=two_years_ago.month,
    )
