# from . import base as xg

from sqlalchemy import util, sql
from sqlalchemy import types as sqltypes, schema as sa_schema
from sqlalchemy.types import VARCHAR, NVARCHAR, CHAR, \
    BLOB, CLOB, DATE, TIME, TIMESTAMP, FLOAT, BIGINT, BINARY, Integer


class NCLOB(sqltypes.Text):
    __visit_name__ = 'CLOB'


class VARCHAR2(VARCHAR):
    __visit_name__ = 'VARCHAR'


NVARCHAR2 = NVARCHAR


class NUMBER(sqltypes.Numeric, sqltypes.Integer):
    __visit_name__ = 'NUMERIC'

    def __init__(self, precision=None, scale=None, asdecimal=None):
        if asdecimal is None:
            asdecimal = bool(scale and scale > 0)

        super(NUMBER, self).__init__(
            precision=precision, scale=scale, asdecimal=asdecimal)

    def adapt(self, impltype):
        ret = super(NUMBER, self).adapt(impltype)
        # leave a hint for the DBAPI handler
        ret._is_xg_number = True
        return ret

    @property
    def _type_affinity(self):
        if bool(self.scale and self.scale > 0):
            return sqltypes.Numeric
        else:
            return sqltypes.Integer


class DOUBLE_PRECISION(sqltypes.Numeric):
    __visit_name__ = 'DOUBLE_PRECISION'

    def __init__(self, precision=None, asdecimal=None):
        if asdecimal is None:
            asdecimal = False

        super(DOUBLE_PRECISION, self).__init__(
            precision=precision, asdecimal=asdecimal)


class LONGVARCHAR(sqltypes.Text):
    __visit_name__ = 'LONGVARCHAR'


class DATE(sqltypes.Date):
    __visit_name__ = 'DATE'

    def _compare_type_affinity(self, other):
        return other._type_affinity in (sqltypes.DateTime, sqltypes.Date)


class TIME(sqltypes.TIME):
    __visit_name__ = 'TIME'

    def __init__(self, timezone=False):
        super(TIME, self).__init__(timezone=timezone)


class DATETIME(sqltypes.DATETIME):
    __visit_name__ = 'DATETIME'


class INTERVAL(sqltypes.TypeEngine):
    __visit_name__ = 'INTERVAL'

    def __init__(self,
                 year_precision=None,
                 to_month=False,
                 month_precision=None,
                 day_precision=None,
                 to_hour=False,
                 to_minute=False,
                 hour_precision=None,
                 minute_precision=None,
                 second_precision=None):
        self.year_precision = year_precision
        self.to_month = to_month
        self.month_precision = month_precision

        self.day_precision = day_precision
        self.to_hour = to_hour
        self.to_minute = to_minute
        self.hour_precision = hour_precision
        self.minute_precision = minute_precision
        self.second_precision = second_precision

    @classmethod
    def _adapt_from_generic_interval(cls, interval):
        return INTERVAL(day_precision=interval.day_precision,
                        second_precision=interval.second_precision)

    @property
    def _type_affinity(self):
        return sqltypes.Interval


class ROWID(sqltypes.TypeEngine):
    __visit_name__ = 'ROWID'


class _XGBoolean(sqltypes.Boolean):
    def get_dbapi_type(self, dbapi):
        return dbapi.NUMBER


class _XGNumeric(sqltypes.Numeric):
    pass


class _XGDate(sqltypes.Date):
    def bind_processor(self, dialect):
        return None

    def result_processor(self, dialect, coltype):
        def process(value):
            return value

        return process


class _LOBMixin(object):
    def result_processor(self, dialect, coltype):
        if not dialect.auto_convert_lobs:
            return None

        def process(value):
            if value is not None:
                if isinstance(value, dialect.dbapi.LOB):
                    return value.read()
                else:
                    return value
            else:
                return value

        return process


class _NativeUnicodeMixin(object):
    pass


# we apply a connection output handler that returns
# unicode in all cases, so the "native_unicode" flag
# will be set for the default String.result_processor.


class _XGChar(_NativeUnicodeMixin, sqltypes.CHAR):
    def get_dbapi_type(self, dbapi):
        return dbapi.FIXED_STRING


class CHARACTER(sqltypes.CHAR):
    pass


class TINYINT(sqltypes.TypeEngine):
    __visit_name__ = 'TINYINT'

    def result_processor(self, dialect, coltype):
        def process(value):
            return value

        return process


class BYTE(TINYINT):
    pass


class DOUBLE(sqltypes.FLOAT):
    pass


class BIT(sqltypes.TypeEngine):
    __visit_name__ = 'BIT'

    def result_processor(self, dialect, coltype):
        def process(value):
            return value

        return process


class TIMESTAMP(sqltypes.TIMESTAMP):
    __visit_name__ = 'XGTIMESTAMP'

    def __init__(self, timezone=False, local_timezone=False):
        self.timezone = timezone
        self.local_timezone = False

        if timezone:
            self.local_timezone = False
        else:
            self.local_timezone = local_timezone

        super(TIMESTAMP, self).__init__(timezone=timezone)


class _XGNVarChar(_NativeUnicodeMixin, sqltypes.NVARCHAR):
    def get_dbapi_type(self, dbapi):
        return getattr(dbapi, 'UNICODE_STRING', dbapi.STRING)


class _XGText(_LOBMixin, sqltypes.Text):
    def get_dbapi_type(self, dbapi):
        return dbapi.CLOB


class IMAGE(sqltypes.TypeEngine):
    __visit_name__ = 'IMAGE'

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is not None:
                if isinstance(value, dialect.dbapi.LOB):
                    return value.read()
                else:
                    return value
            return value

        return process

    def get_dbapi_type(self, dbapi):
        return dbapi.LOB


class _XGLongVarchar(_LOBMixin, LONGVARCHAR):
    def get_dbapi_type(self, dbapi):
        return dbapi.LONG_STRING


class _XGString(_NativeUnicodeMixin, sqltypes.String):
    pass


class _XGEnum(_NativeUnicodeMixin, sqltypes.Enum):
    def bind_processor(self, dialect):
        enum_proc = sqltypes.Enum.bind_processor(self, dialect)
        if util.py2k:
            unicode_proc = _NativeUnicodeMixin.bind_processor(self, dialect)
        else:
            unicode_proc = None

        def process(value):
            raw_str = enum_proc(value)
            if unicode_proc:
                raw_str = unicode_proc(raw_str)
            return raw_str

        return process


class _XGUnicodeText(
    _LOBMixin, _NativeUnicodeMixin, sqltypes.UnicodeText):
    def get_dbapi_type(self, dbapi):
        return dbapi.CLOB

    def result_processor(self, dialect, coltype):
        lob_processor = _LOBMixin.result_processor(self, dialect, coltype)
        if lob_processor is None:
            return None

        string_processor = sqltypes.UnicodeText.result_processor(
            self, dialect, coltype)

        if string_processor is None:
            return lob_processor
        else:
            def process(value):
                return string_processor(lob_processor(value))

            return process


class _XGInteger(sqltypes.Integer):
    def result_processor(self, dialect, coltype):
        def to_int(val):
            if val is not None:
                val = int(val)
            return val

        return to_int


class XGBINARY(sqltypes.BINARY):
    def get_dbapi_type(self, dbapi):
        self.dbapi = dbapi
        return dbapi.BINARY

    def bind_processor(self, dialect):
        def process(value):
            if isinstance(value, dialect.dbapi.LOB):
                return value.read()

            if type(value) is dialect.dbapi.LOB:
                return value.read()

            if type(value) is bytes:
                return bytes(value)

            return str(value)

        return process


class _XGBinary(sqltypes._Binary):
    def get_dbapi_type(self, dbapi):
        self.dbapi = dbapi
        return dbapi.BINARY

    def bind_processor(self, dialect):
        def process(value):
            if isinstance(value, dialect.dbapi.LOB):
                return value.read()

            if type(value) is dialect.dbapi.LOB:
                return value.read()

            if type(value) is bytes:
                return bytes(value)

            return str(value)

        return process

    def result_processor(self, dialect, coltype):
        if not dialect.auto_convert_lobs:
            return None

        def process(value):
            if isinstance(value, dialect.dbapi.LOB):
                return value.read()

            if type(value) is dialect.dbapi.LOB:
                return value.read()

            if type(value) is bytes:
                return bytes(value)

            return str(value)

        return process


class _XGInterval(INTERVAL):
    def get_dbapi_type(self, dbapi):
        return dbapi.INTERVAL


class _XGRowid(ROWID):
    def get_dbapi_type(self, dbapi):
        return dbapi.ROWID


colspecs = {
    sqltypes.Boolean: _XGBoolean,
    sqltypes.Interval: INTERVAL,
    sqltypes.DateTime: DATE,
    sqltypes.Time: TIME,
    sqltypes.BINARY: _XGBinary
}

ischema_names = {
    'VARCHAR': VARCHAR,
    'CHAR': CHAR,
    'DATE': DATE,
    'DATETIME': DATETIME,
    'DATETIME WITH TIME ZONE': DATETIME,
    'NUMBER': NUMBER,
    'BLOB': BLOB,
    'CLOB': CLOB,
    'TIME WITH TIME ZONE': TIME,
    'TIMESTAMP': TIMESTAMP,
    'TIMESTAMP WITH TIME ZONE': TIMESTAMP,
    'INTERVAL DAY TO SECOND': INTERVAL,
    'FLOAT': FLOAT,
    'DOUBLE': DOUBLE,
    'LONG': LONGVARCHAR,
    'BIT': BIT,
    'INTEGER': Integer,
    'INT': Integer,
    'BINARY': BINARY
}
