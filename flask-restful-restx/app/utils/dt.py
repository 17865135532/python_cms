from datetime import timedelta, datetime
import calendar

from app import constants
from app.utils.types import enum_item2val


def is_month_range(tax_start, tax_end):
    if tax_start.day != 1:
        return False
    if tax_start.month != tax_end.month or tax_start.year != tax_end.year:
        return False
    month_end = (tax_start + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    return month_end.day == tax_end.day


def is_quarter_range(tax_start, tax_end):
    if tax_start.day != 1:
        return False
    if tax_start.month not in [1, 4, 7, 10]:
        return False
    if tax_start.month + 2 != tax_end.month or tax_start.year != tax_end.year:
        return False
    quarter_end = (tax_start + timedelta(days=93)).replace(day=1) - timedelta(days=1)
    return quarter_end.day == tax_end.day


def is_half_year_range(tax_start, tax_end):
    if tax_start.day != 1:
        return False
    if tax_start.year != tax_end.year:
        return False
    if tax_start.month == 1:
        return tax_end.month == 6 and tax_end.day == 30
    elif tax_start.month == 7:
        return tax_end.month == 12 and tax_end.day == 31
    return False


def is_year_range(tax_start, tax_end):
    return all([
        tax_start.year == tax_end.year,
        tax_start.month == 1,
        tax_start.day == 1,
        tax_end.month == 12,
        tax_end.day == 31
    ])


def ensure_datetime(o, format="%Y-%m-%d %H:%M:%S"):
    if isinstance(o, str):
        return datetime.strptime(o, format)
    elif isinstance(o, datetime):
        return o
    else:
        return o


def get_month_date(today):
    today = ensure_datetime(today)
    year = today.year
    month = today.month
    start_day = 1
    if today.month == 1:
        year = today.year - 1
        month = 12
        _, last_day = calendar.monthrange(today.year - 1, month)
    else:
        _, last_day = calendar.monthrange(year, month)
    return datetime(year, month, start_day), datetime(year, month, last_day)


def get_lastseason_date(today):
    today = ensure_datetime(today)
    quarter = int((today.month - 1) / 3 + 1)
    year = today.year
    start_day = 1
    stop_day = 31
    if quarter == 1:
        year = year - 1
        month = 12
    elif quarter == 2:
        year = today.year
        month = 3
    elif quarter == 3:
        month = 6
        stop_day = 30
    else:
        month = 9
        stop_day = 30

    return datetime(year, month-3, start_day), datetime(year, month, stop_day)


def get_year_date(today):
    today = ensure_datetime(today)
    return datetime(today.year-1, 1, 1), datetime(today.year-1, 12, 31)


def get_half_year_date(today):
    today = ensure_datetime(today)
    if today.month <= 5:
        return datetime(today.year-1, 6, 1), datetime(today.year-1, 12, 31)
    else:
        return datetime(today.year, 1, 1), datetime(today.year, 5, 31)


def get_declaration_period(frequency, today):

    if enum_item2val(constants.DeclarationPeriod, frequency) == "year":
        return get_year_date(today)
    if enum_item2val(constants.DeclarationPeriod, frequency) == "quarter":
        return get_lastseason_date(today)
    if enum_item2val(constants.DeclarationPeriod, frequency) == "month":
        return get_month_date(today)
    if enum_item2val(constants.DeclarationPeriod, frequency) == "count":
        return get_month_date(today)
    if enum_item2val(constants.DeclarationPeriod, frequency) == "half_year":
        return get_half_year_date(today)


if __name__ == '__main__':
    print(is_month_range(datetime(2020,7,1), datetime(2020,7,31)))
