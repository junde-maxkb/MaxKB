from __future__ import absolute_import

from .base import XGCompiler, XGDialect, XGExecutionContext
from . import base as xg
import sqlalchemy.engine.result as _result
from sqlalchemy import types as sqltypes, util, exc
from sqlalchemy import util
import random
import collections
import decimal
import re
import time
import datetime as dt
from .types import _XGBinary, _XGBoolean, _XGChar, _XGDate, _XGEnum, \
    _XGInteger, _XGInterval, _XGLongVarchar, _XGNumeric, \
    _XGNVarChar, _XGRowid, _XGString, _XGText, _XGUnicodeText, INTERVAL, \
    LONGVARCHAR, ROWID, XGBINARY


class XGCompiler_xgPython(XGCompiler):
    pass
    # def bindparam_string(self, name, **kw):
    #     self.dialect.trace_process('XGCompiler_xgPython', 'bindparam_string', name, **kw)
    #
    #     quote = getattr(name, 'quote', None)
    #     if quote is True or quote is not False and \
    #             self.preparer._bindparam_requires_quotes(name):
    #         quoted_name = '"%s"' % name
    #         self._quoted_bind_names[name] = quoted_name
    #         return XGCompiler.bindparam_string(self, quoted_name, **kw)
    #     else:
    #         return XGCompiler.bindparam_string(self, name, **kw)


class XGExecutionContext_xgPython(XGExecutionContext):

    def pre_exec(self):
        self.dialect.trace_process('XGExecutionContext_xgPython', 'pre_exec')

        if not getattr(self.compiled, "_xg_sql_compiler", False):
            return

        self.out_parameters = {}

        self.include_set_input_sizes = self.dialect._include_setinputsizes

    def create_cursor(self):
        self.dialect.trace_process('XGExecutionContext_xgPython', 'create_cursor')

        c = self._dbapi_connection.cursor()
        if self.dialect.arraysize:
            c.arraysize = self.dialect.arraysize

        return c


'''
    def get_result_proxy(self):
        self.dialect.trace_process('XGExecutionContext_xgPython', 'get_result_proxy')
        
        if hasattr(self, 'out_parameters') and self.compiled.returning:
            returning_params = dict(
                (k, v.getvalue())
                for k, v in self.out_parameters.items()
            )
            return ReturningResultProxy(self, returning_params)

        result = None
        if self.cursor.description is not None:
            for column in self.cursor.description:
                type_code = column[1]
                if type_code in self.dialect._xgPython_binary_types:
                    result = _result.BufferedColumnResultProxy(self)

        if result is None:
            result = _result.ResultProxy(self)

        if hasattr(self, 'out_parameters'):
            if self.compiled_parameters is not None and \
                    len(self.compiled_parameters) == 1:
                result.out_parameters = out_parameters = {}

                for bind, name in self.compiled.bind_names.items():
                    if name in self.out_parameters:
                        type = bind.type
                        impl_type = type.dialect_impl(self.dialect)
                        dbapi_type = impl_type.get_dbapi_type(
                            self.dialect.dbapi)
                        result_processor = impl_type.\
                            result_processor(self.dialect,
                                             dbapi_type)
                        if result_processor is not None:
                            out_parameters[name] = \
                                result_processor(
                                    self.out_parameters[name].getvalue())
                        else:
                            out_parameters[name] = self.out_parameters[
                                name].getvalue()
            else:
                result.out_parameters = dict(
                                            (k, v.getvalue())
                    for k, v in self.out_parameters.items()
                )

        return result
'''

'''
class ReturningResultProxy(_result.FullyBufferedResultProxy):
    """Result proxy which stuffs the _returning clause + outparams
    into the fetch."""

    def __init__(self, context, returning_params):
        self._returning_params = returning_params
        super(ReturningResultProxy, self).__init__(context)

    def _cursor_description(self):
        self.dialect.trace_process('ReturningResultProxy', '_cursor_description')
        
        returning = self.context.compiled.returning
        return [
            ("ret_%d" % i, None)
            for i, col in enumerate(returning)
        ]

    def _buffer_rows(self):
        self.dialect.trace_process('ReturningResultProxy', '_buffer_rows')
        
        return collections.deque(
            [tuple(self._returning_params["ret_%d" % i]
                   for i, c in enumerate(self._returning_params))]
        )
'''


class XGDialect_xgPython(XGDialect):
    supports_statement_cache = True
    execution_ctx_cls = XGExecutionContext_xgPython
    statement_compiler = XGCompiler_xgPython

    supports_sane_rowcount = True
    supports_sane_multi_rowcount = False

    supports_unicode_statements = True
    supports_unicode_binds = True

    driver = "xgcondb"

    colspecs = colspecs = {
        sqltypes.Numeric: _XGNumeric,
        sqltypes.Date: _XGDate,
        sqltypes._Binary: _XGBinary,
        sqltypes.Boolean: _XGBoolean,
        sqltypes.BOOLEAN: _XGBoolean,
        sqltypes.Interval: _XGInterval,
        INTERVAL: _XGInterval,
        sqltypes.Text: _XGText,
        sqltypes.TEXT: _XGText,
        sqltypes.String: _XGString,
        sqltypes.UnicodeText: _XGUnicodeText,
        sqltypes.CHAR: _XGChar,
        sqltypes.Enum: _XGEnum,
        sqltypes.BINARY: XGBINARY,

        LONGVARCHAR: _XGLongVarchar,

        sqltypes.Integer: _XGInteger,
        sqltypes.INTEGER: _XGInteger,

        sqltypes.Unicode: _XGNVarChar,
        sqltypes.NVARCHAR: _XGNVarChar,
        ROWID: _XGRowid,
    }

    execute_sequence_format = list

    def __init__(self,
                 # auto_setinputsizes=False,
                 # exclude_setinputsizes=("STRING", "UNICODE"),
                 auto_convert_lobs=True,
                 # threaded=True,
                 # allow_twophase=True,
                 coerce_to_decimal=True,
                 # coerce_to_unicode=False,
                 autocommit=False,
                 connection_timeout=30,
                 arraysize=50,  # _retry_on_12516=False,
                 **kwargs):
        XGDialect.__init__(self, **kwargs)
        # self.threaded = threaded
        self.arraysize = arraysize
        # self.allow_twophase = allow_twophase
        # self.supports_timestamp = self.dbapi is None or \
        #    hasattr(self.dbapi, 'TIMESTAMP')
        # self.auto_setinputsizes = auto_setinputsizes
        self.auto_convert_lobs = auto_convert_lobs
        # self._retry_on_12516 = _retry_on_12516
        self.autocommit = False
        self.connection_timeout = connection_timeout

        if hasattr(self.dbapi, 'version'):
            self.xgPython_ver = '2.3.8'

        else:
            self.xgPython_ver = (0, 0)

        def types(*names):
            return set(
                getattr(self.dbapi, name, None) for name in names
            ).difference([None])

        # self.exclude_setinputsizes = types(*(exclude_setinputsizes or ()))
        self._xgPython_string_types = types("STRING", "UNICODE",
                                            "NCLOB", "CLOB")
        self._xgPython_unicode_types = types("UNICODE", "NCLOB")
        self._xgPython_binary_types = types("CLOB", "NCLOB", "BLOB")

        self.supports_native_decimal = coerce_to_decimal

        if self.xgPython_ver is None or \
                not self.auto_convert_lobs or \
                not hasattr(self.dbapi, 'CLOB'):
            self.dbapi_type_map = {}
        else:
            self.dbapi_type_map = {
                self.dbapi.CLOB: xg.CLOB(),
                # self.dbapi.NCLOB: xg.NCLOB(),
                self.dbapi.BLOB: xg.BLOB(),
            }

    @classmethod
    def dbapi(cls):
        import xgcondb
        return xgcondb

    @classmethod
    def import_dbapi(cls):
        import xgcondb
        return xgcondb

    def connect(self, *cargs, **cparams):
        self.trace_process('XGDialect_xgPython', 'connect', *cargs, **cparams)

        try:
            conn = self.dbapi.connect(*cargs, **cparams)

            # self.encoding = self.get_conn_local_code(conn)
            # 
            # self.case_sensitive = conn.str_case_sensitive
            # if self.case_sensitive:
            #     self.requires_name_normalize = True
            # else:
            #     self.requires_name_normalize = False

            cursor = conn.cursor();
            # cursor.execute('SET_SESSION_IDENTITY_CHECK(1);')
            return conn
        except self.dbapi.DatabaseError as err:
            raise

    def initialize(self, connection):
        self.trace_process('XGDialect_xgPython', 'initialize', connection)
        super(XGDialect_xgPython, self).initialize(connection)
        self._detect_decimal_char(connection)

    def _detect_decimal_char(self, connection):
        self.trace_process('XGDialect_xgPython', '_detect_decimal_char', connection)
        return

    def _detect_decimal(self, value):
        self.trace_process('XGDialect_xgPython', '_detect_decimal', value)

        if "." in value:
            return decimal.Decimal(value)
        else:
            return int(value)

    _to_decimal = decimal.Decimal

    def on_connect(self):
        self.trace_process('XGDialect_xgPython', 'on_connect')
        return

    def create_connect_args(self, url):
        self.trace_process('XGDialect_xgPython', 'create_connect_args', url)

        opts = url.translate_connect_args(username='user')

        opts.update(url.query)

        util.coerce_kw_type(opts, 'access_mode', int)
        util.coerce_kw_type(opts, 'autoCommit', bool)
        util.coerce_kw_type(opts, 'connection_timeout', int)
        util.coerce_kw_type(opts, 'login_timeout', int)
        util.coerce_kw_type(opts, 'txn_isolation', int)
        util.coerce_kw_type(opts, 'compress_msg', bool)
        util.coerce_kw_type(opts, 'use_stmt_pool', bool)
        util.coerce_kw_type(opts, 'ssl_path', str)
        util.coerce_kw_type(opts, 'mpp_login', bool)
        util.coerce_kw_type(opts, 'rwseparate', bool)
        util.coerce_kw_type(opts, 'rwseparate_percent', int)
        util.coerce_kw_type(opts, 'lang_id', int)
        util.coerce_kw_type(opts, 'local_code', int)

        opts.setdefault('autoCommit', self.autocommit)
        opts.setdefault('connection_timeout', self.connection_timeout)
        opts.setdefault('host', 'localhost')
        opts.setdefault('port', 5236)

        dsn = opts['host'] + ':%d' % opts['port']

        if dsn is not None:
            opts['dsn'] = dsn

        return ([], opts)

    def _get_server_version_info(self, connection):
        return (12, 1, 1, 0)

    def is_disconnect(self, e, connection, cursor):
        self.trace_process('XGDialect_xgPython', 'is_disconnect', e, connection, cursor)

        error, = e.args
        if isinstance(e, self.dbapi.InterfaceError):
            return "not connected" in str(e)
        elif hasattr(error, 'code'):
            return error.code in (-70025, -70028, -6010, -70019)
        else:
            return False

    def create_xid(self):
        self.trace_process('XGDialect_xgPython', 'create_xid')

        """create a two-phase transaction ID.

        this id will be passed to do_begin_twophase(), do_rollback_twophase(),
        do_commit_twophase().  its format is unspecified."""

        id = random.randint(0, 2 ** 128)
        return (0x1234, "%032x" % id, "%032x" % 9)

    def do_executemany(self, cursor, statement, parameters, context=None):
        self.trace_process('XGDialect_xgPython', 'do_executemany', cursor, statement, parameters, context)

        if isinstance(parameters, tuple):
            parameters = list(parameters)
        cursor.executemany(statement, parameters)

    def do_rollback_twophase(self, connection, xid, is_prepared=True,
                             recover=False):
        self.trace_process('XGDialect_xgPython', 'do_rollback_twophase', connection, xid, is_prepared, recover)

        self.do_rollback(connection.connection)

    def do_commit_twophase(self, connection, xid, is_prepared=True,
                           recover=False):
        self.trace_process('XGDialect_xgPython', 'do_commit_twophase', connection, xid, is_prepared, recover)

        self.do_commit(connection.connection)


dialect = XGDialect_xgPython
