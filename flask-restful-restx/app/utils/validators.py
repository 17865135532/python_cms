import logging
import datetime

from jsonschema import Draft4Validator, validators, ValidationError


logger = logging.getLogger()


def is_number(validator, value, instance, schema):
    if not isinstance(instance, str):
        yield ValidationError("%r is not a string" % instance)
    try:
        float(instance)
        if value is False:
            yield ValidationError("%r is a number" % instance)
    except ValueError:
        if value is True:
            yield ValidationError("%r is not a number" % instance)


def check_max_bytes_len(validator, value, instance, schema):
    if not isinstance(instance, str):
        yield ValidationError("%r is not a string" % instance)
    if len(instance.encode('gbk')) > value:
        yield ValidationError('%r is too long' % instance)


def is_date(validator, value, instance, schema):
    if not isinstance(instance, (str, datetime.datetime)):
        yield ValidationError('%r is not date' % instance)
    try:
        if isinstance(instance, str):
            datetime.datetime.strptime(instance, "%Y-%m-%d")
    except ValueError:
        if value is True:
            yield ValidationError("%r is not a date" % instance)


MyValidator = validators.extend(
    Draft4Validator,
    {'is_number': is_number, 'max_bytes_len': check_max_bytes_len, 'is_date': is_date}
)
