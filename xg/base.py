import re
from sqlalchemy import util, sql,text
from sqlalchemy.engine import default, reflection
from sqlalchemy.sql import compiler, visitors, expression, util as sql_util
from sqlalchemy.sql import operators as sql_operators
from sqlalchemy.sql.elements import quoted_name
from sqlalchemy import types as sqltypes, schema as sa_schema
from sqlalchemy.types import VARCHAR, NVARCHAR, CHAR, \
    BLOB, CLOB, TIME, TIMESTAMP, FLOAT, BIGINT
from .types import NUMBER
from .types import colspecs, ischema_names
import sqlalchemy.sql.elements
from datetime import datetime
NO_ARG = util.symbol("NO_ARG")

RESERVED_WORDS = \
    set('SHARE RAW DROP BETWEEN FROM DESC OPTION PRIOR LONG THEN '
        'DEFAULT ALTER IS INTO MINUS INTEGER NUMBER GRANT IDENTIFIED '
        'ALL TO ORDER ON FLOAT DATE HAVING CLUSTER NOWAIT RESOURCE '
        'ANY TABLE INDEX FOR UPDATE WHERE CHECK SMALLINT WITH DELETE '
        'BY ASC REVOKE LIKE SIZE RENAME NOCOMPRESS NULL GROUP VALUES '
        'AS IN VIEW EXCLUSIVE COMPRESS SYNONYM SELECT INSERT EXISTS '
        'NOT TRIGGER ELSE CREATE INTERSECT PCTFREE DISTINCT USER '
        'CONNECT SET MODE OF UNIQUE VARCHAR2 VARCHAR LOCK OR CHAR '
        'DECIMAL UNION PUBLIC AND START UID COMMENT CURRENT LEVEL '
        'SCHEMA ROWS LIMIT YEAR DATETIME NUMBER'.split())

NO_ARG_FNS = set('UID CURRENT_DATE SYSDATE USER '
                 'CURRENT_TIME CURRENT_TIMESTAMP'.split())

class XGTypeCompiler(compiler.GenericTypeCompiler):

    def visit_TINYINT(self, type_, **kw):
        return "TINYINT"
    
    def visit_BIT(self, type_, **kw):
        self.dialect.trace_process('XGTypeCompiler', 'visit_BIT', type_, **kw)
        return "BIT"

    def visit_unicode(self, type_, **kw):
        self.dialect.trace_process('XGTypeCompiler', 'visit_unicode', type_, **kw)
        
        if self.dialect._supports_nchar:
            return self.visit_NVARCHAR2(type_, **kw)
        else:
            return self.visit_VARCHAR2(type_, **kw)

    def visit_INTERVAL(self, type_, **kw):
        self.dialect.trace_process('XGTypeCompiler', 'visit_INTERVAL', type_, **kw)
        
        # INTERVAL YEAR
        if type_.year_precision is not None and type_.to_month:
            return "INTERVAL YEAR TO MONTH"
        elif type_.year_precision is not None and not type_.to_month:
            return "INTERVAL YEAR"
        
        # INTERVAL MONTH
        elif type_.month_precision:
            return "INTERVAL MONTH"
        
        # INTERVAL DAY
        elif type_.day_precision is not None and type_.to_hour:
            return "INTERVAL DAY TO HOUR"
        elif type_.day_precision is not None and type_.to_minute:
            return "INTERVAL DAY TO MINUTE"
        elif type_.day_precision is not None and type_.second_precision is not None:
            return "INTERVAL DAY TO SECOND"
        elif type_.day_precision is not None:
            return "INTERVAL DAY"
        
        #INTERVAL HOUR
        elif type_.hour_precision is not None and type_.to_minute:
            return "INTERVAL HOUR TO MINUTE"
        elif type_.hour_precision is not None and type_.second_precision is not None:
            return "INTERVAL HOUR TO SECOND"
        elif type_.hour_precision is not None:
            return "INTERVAL HOUR"
        
        #INTERVAL MINUTE
        elif type_.minute_precision is not None and type_.second_precision is not None:
            return "INTERVAL MINUTE TO SECOND"
        elif type_.minute_precision is not None:
            return "INTERVAL MINUTE"
        
        #INTERVAL SECOND
        elif type_.second_precision is not None:
            return "INTERVAL SECOND"
        else:
            return "INTERVAL DAY"

    def visit_LONGVARCHAR(self, type_, **kw):
        return "VARCHAR"

    def visit_TIMESTAMP(self, type_, **kw):
        if type_.timezone:
            return "TIMESTAMP WITH TIME ZONE"
        else:
            return "TIMESTAMP"
        
    def visit_XGTIMESTAMP(self, type_, **kw):
        self.dialect.trace_process('XGTypeCompiler', 'visit_XGTIMESTAMP', type_, **kw)
        
        if type_.timezone:
            return "TIMESTAMP WITH TIME ZONE"
        elif type_.local_timezone:
            return "TIMESTAMP WITH TIME ZONE"
        else:
            return "TIMESTAMP"
    
    def visit_TIME(self, type_, **kw):
        self.dialect.trace_process('XGTypeCompiler', 'visit_TIME', type_, **kw)
        
        if type_.timezone:
            return "TIME WITH TIME ZONE"
        else:
            return "TIME"
    
    def visit_IMAGE(self, type_, **kw):
        return "BLOB"

    def visit_DOUBLE_PRECISION(self, type_, **kw):
        self.dialect.trace_process('XGTypeCompiler', 'visit_DOUBLE_PRECISION', type_, **kw)
        return self._generate_numeric(type_, "DOUBLE", **kw)

    def visit_NUMBER(self, type_, **kw):
        self.dialect.trace_process('XGTypeCompiler', 'visit_NUMBER', type_, **kw)
        return self._generate_numeric(type_, "NUMBER", **kw)

    def _generate_numeric(self, type_, name, precision=None, scale=None, **kw):
        self.dialect.trace_process('XGTypeCompiler', '_generate_numeric', type_, name, precision=None, scale=None, **kw)
        
        if precision is None:
            precision = type_.precision

        if scale is None:
            scale = getattr(type_, 'scale', None)

        if precision is None:
            return name
        elif scale is None:
            n = "%(name)s(%(precision)s)"
            return n % {'name': name, 'precision': precision}
        else:
            n = "%(name)s(%(precision)s, %(scale)s)"
            return n % {'name': name, 'precision': precision, 'scale': scale}

    def visit_string(self, type_, **kw):
        self.dialect.trace_process('XGTypeCompiler', 'visit_string', type_, **kw)
        return self.visit_VARCHAR2(type_, **kw)

    def visit_VARCHAR2(self, type_, **kw):
        self.dialect.trace_process('XGTypeCompiler', 'visit_VARCHAR2', type_, **kw)
        return self._visit_varchar(type_, '', '')

    def visit_NVARCHAR2(self, type_, **kw):
        self.dialect.trace_process('XGTypeCompiler', 'visit_NVARCHAR2', type_, **kw)
        return self._visit_varchar(type_, '', '')
    visit_NVARCHAR = visit_NVARCHAR2

    def visit_VARCHAR(self, type_, **kw):
        self.dialect.trace_process('XGTypeCompiler', 'visit_VARCHAR', type_, **kw)
        return self._visit_varchar(type_, '', '')
    
    def visit_LongVarBinary(self, type_, **kw):
        self.dialect.trace_process('XGTypeCompiler', 'visit_LongVarBinary', type_, **kw)
        return "LONGVARBINARY"

    def _visit_varchar(self, type_, n, num):
        self.dialect.trace_process('XGTypeCompiler', '_visit_varchar', type_, n, num)
        if not type_.length:
            return "VARCHAR%"
        else:
            varchar = "VARCHAR(%(length)s )"
            return varchar % {'length': type_.length}

    def visit_text(self, type_, **kw):
        self.dialect.trace_process('XGTypeCompiler', 'visit_text', type_, **kw)
        return "VARCHAR"

    def visit_unicode_text(self, type_, **kw):
        if self.dialect._supports_nchar:
            return self.visit_NCLOB(type_, **kw)
        else:
            return self.visit_CLOB(type_, **kw)


    def visit_ROWID(self, type_, **kw):
        return "ROWID"

    def visit_NCLOB(self, type_, **kw):
        return "CLOB"

class XGCompiler(compiler.SQLCompiler):
    compound_keywords = util.update_copy(
        compiler.SQLCompiler.compound_keywords,
        {
            expression.CompoundSelect.EXCEPT: 'MINUS'
        }
    )

    def __init__(self, *args, **kwargs):
        self.__wheres = {}
        self._quoted_bind_names = {}
        super(XGCompiler, self).__init__(*args, **kwargs)

    def visit_mod_binary(self, binary, operator, **kw):
        return "mod(%s, %s)" % (self.process(binary.left, **kw),
                                self.process(binary.right, **kw))

    def visit_now_func(self, fn, **kw):
        return "CURRENT_TIMESTAMP"

    def visit_char_length_func(self, fn, **kw):
        return "LENGTH" + self.function_argspec(fn, **kw)

    def visit_match_op_binary(self, binary, operator, **kw):
        return "CONTAINS (%s, %s)" % (self.process(binary.left),
                                      self.process(binary.right))

    def visit_true(self, expr, **kw):
        return '1'

    def visit_false(self, expr, **kw):
        return '0'

    def get_cte_preamble(self, recursive):
        return "WITH"

    def get_select_hint_text(self, byfroms):
        return " ".join(
            "/*+ %s */" % text for table, text in byfroms.items()
        )

    def function_argspec(self, fn, **kw):
        if len(fn.clauses) > 0 or fn.name.upper() not in NO_ARG_FNS:
            return compiler.SQLCompiler.function_argspec(self, fn, **kw)
        else:
            return ""

    def default_from(self):
        return " FROM DUAL"
    
    def _generate_generic_unary_operator(self, unary, opstring, **kw):
        if opstring == 'EXISTS ':
            rs = 'SELECT COUNT(*) FROM ' + unary.element._compiler_dispatch(self, **kw)
            return 'CASE WHEN (' + rs + ' AS R_EXISTS) > 0 THEN 1 ELSE 0 END '
        return opstring + unary.element._compiler_dispatch(self, **kw)    

    def visit_join(self, join, from_linter=None, **kwargs):

        if self.dialect.use_ansi:
            return compiler.SQLCompiler.visit_join(
                self, join, from_linter=from_linter, **kwargs
            )
        else:
            if from_linter:
                from_linter.edges.add((join.left, join.right))

            kwargs["asfrom"] = True
            if isinstance(join.right, expression.FromGrouping):
                right = join.right.element
            else:
                right = join.right
            return (
                self.process(join.left, from_linter=from_linter, **kwargs)
                + ", "
                + self.process(right, from_linter=from_linter, **kwargs)
            )


    def visit_outer_join_column(self, vc, **kw):
        self.dialect.trace_process('XGCompiler', 'visit_outer_join_column', vc, **kw)
        return self.process(vc.column, **kw) + "(+)"

    def visit_sequence(self, seq, **kw):
        self.dialect.trace_process('XGCompiler', 'visit_sequence', seq, **kw)
        return self.preparer.format_sequence(seq) + ".nextval"

    def get_render_as_alias_suffix(self, alias_name_text):
        self.dialect.trace_process('XGCompiler', 'get_render_as_alias_suffix', alias_name_text)
        return " " + alias_name_text


    def _TODO_visit_compound_select(self, select):
        """Need to determine how to get ``LIMIT``/``OFFSET`` into a
        ``UNION`` for Oracle.
        """
        pass




    def for_update_clause(self, select, **kw):

        if self.is_subquery():
            return ""

        tmp = ' FOR UPDATE'

        if select._for_update_arg.of:
            tmp += ' OF ' + ', '.join(
                self.process(elem, **kw) for elem in
                select._for_update_arg.of
            )

        if select._for_update_arg.nowait:
            tmp += " NOWAIT"
        if select._for_update_arg.skip_locked:
            tmp += " SKIP LOCKED"

        return tmp
    


class XGDDLCompiler(compiler.DDLCompiler):
    
    def get_column_specification(self, column, **kwargs):
        self.dialect.trace_process('XGDDLCompiler', 'get_column_specification', column, **kwargs)
        
        colspec = self.preparer.format_column(column) + " " + \
            self.dialect.type_compiler.process(
                column.type, type_expression=column)
        default = self.get_column_default_string(column)
        
        if column.table is not None \
                and column is column.table._autoincrement_column and \
                column.server_default is None:
            colspec += " IDENTITY(1,1)"  
        
        if default is not None:
            colspec += " DEFAULT " + default

        if not column.nullable:
            colspec += " NOT NULL"
            
        #if column.table is not None and \
        #        column.autoincrement and \
        #        column.autoincrement != 'auto' and \
        #        column.primary_key and \
        #        column.server_default is None:
        #    colspec += " IDENTITY(1,1)"    
            
  
            
        return colspec        

    def define_constraint_cascades(self, constraint):
        self.dialect.trace_process('XGDDLCompiler', 'define_constraint_cascades', constraint)
        
        text = ""
        if constraint.ondelete is not None:
            text += " ON DELETE %s" % constraint.ondelete

        if constraint.onupdate is not None:
            text += " ON UPDATE %s" % constraint.onupdate        

        return text
    
    def visit_unique_constraint(self, constraint, **kw):
        self.dialect.trace_process('XGDDLCompiler', 'visit_unique_constraint', constraint, **kw)
        
        if len(constraint) == 0:
            return ''
        text = ""
        if constraint.name is not None:
            formatted_name = self.preparer.format_constraint(constraint)
            text += "CONSTRAINT %s " % formatted_name
        else:
            formatted_name = "".join("%s_%s_" % (c.table,c.name)
                                     for c in constraint)
            formatted_name += "key"
            text += "CONSTRAINT %s " % formatted_name
            
        text += "UNIQUE (%s)" % (
                ', '.join(self.preparer.quote(c.name)
                              for c in constraint))
        text += self.define_constraint_deferrability(constraint)
        return text    

    def visit_create_index(self, create, include_schema=False, include_table_schema=True, **kw):
        self.dialect.trace_process('XGDDLCompiler', 'visit_create_index', create, include_schema, include_table_schema, **kw)
        
        index = create.element
        self._verify_index_table(index)
        preparer = self.preparer
        text = "CREATE "
        if index.unique:
            text += "UNIQUE "
        if index.dialect_options['xg']['bitmap']:
            text += "BITMAP "
        text += "INDEX %s ON %s (%s)" % (
            self._prepared_index_name(index, include_schema=True),
            preparer.format_table(index.table, use_schema=True),
            ', '.join(
                self.sql_compiler.process(
                    expr,
                    include_table=False, literal_binds=True)
                for expr in index.expressions)
        )
        if index.dialect_options['xg']['compress'] is not False:
            if index.dialect_options['xg']['compress'] is True:
                text += " COMPRESS"
            else:
                text += " COMPRESS %d" % (
                    index.dialect_options['xg']['compress']
                )
        return text

    def post_create_table(self, table):
        self.dialect.trace_process('XGDDLCompiler', 'post_create_table', table)
        
        table_opts = []
        opts = table.dialect_options['xg']

        if opts['on_commit']:
            on_commit_options = opts['on_commit'].replace("_", " ").upper()
            table_opts.append('\n ON COMMIT %s' % on_commit_options)

        if opts['compress']:
            if opts['compress'] is True:
                table_opts.append("\n COMPRESS")
            else:
                table_opts.append("\n COMPRESS FOR %s" % (
                    opts['compress']
                ))

        return ''.join(table_opts)
    


class XGIdentifierPreparer(compiler.IdentifierPreparer):

    reserved_words = set([x.lower() for x in RESERVED_WORDS])
    illegal_initial_characters = set(
        (str(dig) for dig in range(0, 10))).union(["_", "$"])

    def _bindparam_requires_quotes(self, value):
        self.dialect.trace_process('XGIdentifierPreparer', '_bindparam_requires_quotes', value)
        
        """Return True if the given identifier requires quoting."""
        lc_value = value.lower()
        return (lc_value in self.reserved_words
                or value[0] in self.illegal_initial_characters
                or not self.legal_characters.match(str(value))
                )

    def format_savepoint(self, savepoint):
        self.dialect.trace_process('XGIdentifierPreparer', '_bindparam_requires_quotes', savepoint)
        
        name = savepoint.ident.lstrip('_')
        return super(
            XGIdentifierPreparer, self).format_savepoint(savepoint, name)
    
    def _quote_free_identifiers(self, *ids):
        self.dialect.trace_process('XGIdentifierPreparer', '_bindparam_requires_quotes', *ids)
        
        """Unilaterally identifier-quote any number of strings."""
    
        return tuple([self.quote_identifier(i) for i in ids if i is not None])
    
    # for trace only
    def format_alias(self, alias, name=None):
        self.dialect.trace_process('XGIdentifierPreparer', 'format_alias', alias, name)
        return super(XGIdentifierPreparer, self).format_alias(alias, name)
        
    #def format_column(self, column, use_table=False,
                      #name=None, table_name=None):
        #self.dialect.trace_process('XGIdentifierPreparer', 'format_column', column, use_table, name, table_name)
        #return super(XGIdentifierPreparer, self).format_column(column, use_table, name, table_name)
        
    #def format_constraint(self, naming, constraint):
        #self.dialect.trace_process('XGIdentifierPreparer', 'format_constraint', naming, constraint)
        #return super(XGIdentifierPreparer, self).format_constraint(naming, constraint)
        
    def format_label(self, label, name=None):
        self.dialect.trace_process('XGIdentifierPreparer', 'format_label', label, name)
        return super(XGIdentifierPreparer, self).format_label(label, name)
        
    def format_schema(self, name):
        self.dialect.trace_process('XGIdentifierPreparer', 'format_schema', name)
        return super(XGIdentifierPreparer, self).format_schema(name)
        
    def format_sequence(self, sequence, use_schema=True):
        self.dialect.trace_process('XGIdentifierPreparer', 'format_sequence', sequence, use_schema)
        return super(XGIdentifierPreparer, self).format_sequence(sequence, use_schema)
        
    def format_table(self, table, use_schema=True, name=None):
        self.dialect.trace_process('XGIdentifierPreparer', 'format_table', table, use_schema, name)
        return super(XGIdentifierPreparer, self).format_table(table, use_schema, name)
        
    def format_table_seq(self, table, use_schema=True):
        self.dialect.trace_process('XGIdentifierPreparer', 'format_table_seq', table, use_schema)
        return super(XGIdentifierPreparer, self).format_table_seq(table, use_schema)
        

class XGExecutionContext(default.DefaultExecutionContext):

    def get_lastrowid(self):
        cursor = self.create_cursor()
        cursor.execute("show version;")
        version = cursor.fetchone()[0]
        if version.endswith('11.0.0'):
            rowid = cursor.getResultRowid()
            cursor.execute("SELECT id from " +
                           str(self.compiled.statement.table) +
                           " where rowid = '" + str(rowid) + "';")
        else:
            cursor.execute("select last_insert_id();")

        lastrowid = cursor.fetchone()[0]
        return lastrowid

    def fire_sequence(self, seq, type_):
        self.dialect.trace_process('XGExecutionContext', 'fire_sequence', seq, type_)
        
        return self._execute_scalar(
            "SELECT " +
            self.dialect.identifier_preparer.format_sequence(seq) +
            ".nextval FROM DUAL", type_)
        
    def _set_autoinc_col_from_lastrowid(self, table, autoinc_col, lastrowid):
        self.dialect.trace_process('XGExecutionContext', '_set_autoinc_col_from_lastrowid')
        # statement = "select {} from {} where rowid = {}".format(autoinc_col.name, table.name, lastrowid)
        self.dialect.do_execute(self.cursor, "select last_insert_id();", None, None)
        return self.cursor.fetchone()[0]




class XGDialect(default.DefaultDialect):
    name = 'xg'
    supports_statement_cache = True
    supports_alter = True
    supports_unicode_statements = True
    supports_unicode_binds = True
    max_identifier_length = 128
    max_index_name_length = 128    
    supports_sane_rowcount = True
    supports_sane_multi_rowcount = False

    supports_simple_order_by_label = False
    cte_follows_insert = True

    supports_sequences = True
    sequences_optional = False
    postfetch_lastrowid = True

    default_paramstyle = 'qmark'
    colspecs = colspecs
    ischema_names = ischema_names
    requires_name_normalize = False

    supports_comments = True
    supports_default_values = False
    supports_empty_insert = False
    
    supports_trace = False
    supports_trace_params = False
    outfile = None

    statement_compiler = XGCompiler
    ddl_compiler = XGDDLCompiler
    type_compiler = XGTypeCompiler
    preparer = XGIdentifierPreparer
    execution_ctx_cls = XGExecutionContext

    reflection_options = ('xg_resolve_synonyms', )

    construct_arguments = [
        (sa_schema.Table, {
            "resolve_synonyms": False,
            "on_commit": None,
            "compress": False
        }),
        (sa_schema.Index, {
            "bitmap": False,
            "compress": False
        })
    ]

    def __init__(self,
                 use_ansi=True,
                 optimize_limits=False,
                 use_binds_for_limits=True,
                 supports_trace=False,
                 supports_trace_params=False,                 
                 **kwargs):
        self.supports_trace = supports_trace
        self.supports_trace_params = supports_trace_params        
        default.DefaultDialect.__init__(self, **kwargs)
        self.use_ansi = use_ansi
        self.optimize_limits = optimize_limits
        self.use_binds_for_limits = use_binds_for_limits
        
        if self.supports_trace:
            self.outfile = open('sqlalchemy_xg_trace.log', 'a')

    def initialize(self, connection):
        super(XGDialect, self).initialize(connection)
        self.implicit_returning = False
        self.default_schema_name = self._get_default_database_name(connection)
        
    def trace_process(self, cls_str=None, func_str=None, *args, **kws):
        if not self.supports_trace:
            return
        now = datetime.now().isoformat()
        self.outfile.write('{}\n'.format(now))
        self.outfile.write('clsname:{}\n'.format(cls_str))
        self.outfile.write('funcname:{}\n'.format(func_str))
        
        if self.supports_trace_params:
            self.outfile.write('args:{}\n'.format(args))
            self.outfile.write('kws:{}\n'.format(kws))
            
        self.outfile.write('\n')
    
    @property
    def _supports_table_compression(self):
        self.trace_process('XGDialect', '_supports_table_compression')
        
        return self.server_version_info and \
            self.server_version_info >= (10, 1, )

    @property
    def _supports_table_compress_for(self):
        self.trace_process('XGDialect', '_supports_table_compress_for')
        return self.server_version_info and \
            self.server_version_info >= (11, )

    @property
    def _supports_char_length(self):
        self.trace_process('XGDialect', '_supports_char_length')
        return True

    @property
    def _supports_nchar(self):
        self.trace_process('XGDialect', '_supports_nchar')
        return True
    
    @property
    def dialect_description(self):
        self.trace_process('XGDialect', 'dialect_description')
        return super(XGDialect, self).dialect_description()
        
    def do_close(self, dbapi_connection):
        self.trace_process('XGDialect', 'do_close', dbapi_connection)
        super(XGDialect, self).do_close(dbapi_connection)
        
    def do_commit(self, dbapi_connection):
        self.trace_process('XGDialect', 'do_commit', dbapi_connection)
        super(XGDialect, self).do_commit(dbapi_connection)
        
    def do_execute(self, cursor, statement, parameters, context=None):
        self.trace_process('XGDialect', 'do_execute', cursor, statement, parameters, context)
        super(XGDialect, self).do_execute(cursor, statement, parameters, context)
        
    def do_execute_no_params(self, cursor, statement, context=None):
        self.trace_process('XGDialect', 'do_execute_no_params', cursor, statement, context)
        super(XGDialect, self).do_execute_no_params(cursor, statement, context)

    def do_release_savepoint(self, connection, name):
        self.trace_process('XGDialect', 'do_release_savepoint', connection, name)
        pass
    
    _isolation_lookup = ["READ COMMITTED", "SERIALIZABLE"]

    def get_isolation_level(self, connection):
        self.trace_process('XGDialect', 'get_isolation_level', connection)
        raise NotImplementedError("implemented by xg dialect")

    def get_default_isolation_level(self, dbapi_conn):
        self.trace_process('XGDialect', 'get_default_isolation_level', dbapi_conn)
        try:
            return self.get_isolation_level(dbapi_conn)
        except NotImplementedError:
            raise
        except:
            return "READ COMMITTED"

    def set_isolation_level(self, connection, level):
        self.trace_process('XGDialect', 'set_isolation_level', connection, level)
        raise NotImplementedError("implemented by xg dialect")

    def has_table(self, connection, table_name, schema=None, dblink=None, **kw):
        if not schema:
            schema = self.default_schema_name
        name = self.denormalize_name(table_name),
        schema_name = self.denormalize_name(schema)
        cursor = connection.execute(
            text("SELECT table_name FROM all_tables "
                     "WHERE table_name = :name AND schema_id = (select schema_id from all_schemas where schema_name = :schema_name and db_id = "
                 "(select db_id from all_databases where db_name = current_database) );").bindparams(name=name[0],schema_name=schema_name))
        return cursor.first() is not None


    def has_sequence(self, connection, sequence_name, schema=None):
        self.trace_process('XGDialect', 'has_sequence', connection, sequence_name, schema)
        
        if not schema:
            schema = self.default_schema_name
        cursor = connection.execute(
            sql.text("SELECT SEQ_NAME from all_sequences "
                     "where name = :name AND schema_id = (select schema_id from all_schemas where schema_name = :schema_name and db_id = (select db_id from all_databases where db_name = current_database) ); ").bindparams(
                     name=self.denormalize_name(sequence_name),
                     schema_name=self.denormalize_name(schema)))
        return cursor.first() is not None

    # def normalize_name(self, name):
    #     self.trace_process('XGDialect', 'normalize_name', name)
    #     """convert the given name to lowercase if it is detected as
    #     case insensitive.
    #
    #     this method is only used if the dialect defines
    #     requires_name_normalize=True.
    #
    #     """
    #     if name is None:
    #         return None
    #     if name.upper() == name and not \
    #             self.identifier_preparer._requires_quotes(name.lower()):
    #         return name.lower()
    #     elif name.lower() == name:
    #         return quoted_name(name, quote=True)
    #     else:
    #         return name

    def denormalize_name(self, name):
        self.trace_process('XGDialect', 'denormalize_name', name)
        """convert the given name to a case insensitive identifier
        for the backend if it is an all-lowercase name.

        this method is only used if the dialect defines
        requires_name_normalize=True.

        """
        if name is None:
            return None
        elif name.lower() == name and not \
                self.identifier_preparer._requires_quotes(name.lower()):
            name = name.upper()
        return name

    def _get_default_database_name(self, connection):
        return connection.execute(sql.text('SELECT CURRENT_SCHEMA FROM DUAL')).scalar()

    def _resolve_synonym(self, connection, desired_owner=None,
                         desired_synonym=None, desired_table=None):
        self.trace_process('XGDialect', '_resolve_synonym', 
                           connection, desired_owner, desired_synonym, desired_table)
        """search for a local synonym matching the given desired owner/name.

        if desired_owner is None, attempts to locate a distinct owner.

        returns the actual name, owner, dblink name, and synonym name if
        found.
        """

        q = "SELECT owner, table_owner, table_name, db_link, "\
            "synonym_name FROM all_synonyms WHERE "
        clauses = []
        params = {}
        if desired_synonym:
            clauses.append("synonym_name = :synonym_name")
            params['synonym_name'] = desired_synonym
        if desired_owner:
            clauses.append("owner = :desired_owner")
            params['desired_owner'] = desired_owner
        if desired_table:
            clauses.append("table_name = :tname")
            params['tname'] = desired_table

        q += " AND ".join(clauses)

        result = connection.execute(sql.text(q), **params)
        if desired_owner:
            row = result.first()
            if row:
                return (row['table_name'], row['table_owner'],
                        row['db_link'], row['synonym_name'])
            else:
                return None, None, None, None
        else:
            rows = result.fetchall()
            if len(rows) > 1:
                raise AssertionError(
                    "There are multiple tables visible to the schema, you "
                    "must specify owner")
            elif len(rows) == 1:
                row = rows[0]
                return (row['table_name'], row['table_owner'],
                        row['db_link'], row['synonym_name'])
            else:
                return None, None, None, None

    @reflection.cache
    def _prepare_reflection_args(self, connection, table_name, schema=None,
                                 resolve_synonyms=False, dblink='', **kw):
        self.trace_process('XGDialect', '_prepare_reflection_args',
                           connection, table_name, schema,
                           resolve_synonyms, dblink, **kw)

        if resolve_synonyms:
            actual_name, owner, dblink, synonym = self._resolve_synonym(
                connection,
                desired_owner=self.denormalize_name(schema),
                desired_synonym=self.denormalize_name(table_name)
            )
        else:
            actual_name, owner, dblink, synonym = None, None, None, None
        if not actual_name:
            actual_name = self.denormalize_name(table_name)

        if dblink:
            owner = connection.scalar(
                sql.text("SELECT username FROM user_db_links "
                         "WHERE db_link=:link"), link=dblink)
            dblink = "@" + dblink
        elif not owner:
            owner = self.denormalize_name(schema or self.default_schema_name)

        return (actual_name, owner, dblink or '', synonym)

    @reflection.cache
    def get_schema_names(self, connection, **kw):
        self.trace_process('XGDialect', 'get_schema_names', connection, **kw)
        
        s = "select schema_name FROM all_schemas;"
        cursor = connection.exec_driver_sql(s)
        return [row[0] for row in cursor]

    @reflection.cache
    def get_table_names(self, connection, schema=None, **kw):
        self.trace_process('XGDialect', 'get_table_names', connection, schema, **kw)
        
        schema = self.denormalize_name(schema or self.default_schema_name)

        # note that table_names() isn't loading DBLINKed or synonym'ed tables
        if schema is None:
            schema = self.default_schema_name
        cursor = connection.execute(text("SELECT table_name FROM all_tables "
             "WHERE schema_id = (select schema_id from all_schemas where schema_name = :schema_name "
                                                 "and db_id = (select db_id from all_databases where db_name = current_database) );").bindparams(
             schema_name=schema))
        return [row[0] for row in cursor]

    @reflection.cache
    def get_view_names(self, connection, schema=None, **kw):
        self.trace_process('XGDialect', 'get_view_names', connection, schema, **kw)
        
        schema = self.denormalize_name(schema or self.default_schema_name)
        s = sql.text("SELECT view_name FROM all_views where schema_id = (select schema_id from all_schemas where schema_name = :schema_name and db_id = (select db_id from all_databases where db_name = current_database) );")
        cursor = connection.execute(s.bindparams(owner=self.denormalize_name(schema)))
        return [(row[0] for row in cursor)]

    @reflection.cache
    def get_table_options(self, connection, table_name, schema=None, **kw):
        self.trace_process('XGDialect', 'get_table_options', connection, table_name, schema, **kw)
        
        options = {}

        resolve_synonyms = kw.get('xg_resolve_synonyms', False)
        dblink = kw.get('dblink', '')
        info_cache = kw.get('info_cache')

        (table_name, schema, dblink, synonym) = \
            self._prepare_reflection_args(connection, table_name, schema,
                                          resolve_synonyms, dblink,
                                          info_cache=info_cache)
        

        columns = ["table_name"]
        if self._supports_table_compression:
            columns.append("compression")
        if self._supports_table_compress_for:
            columns.append("compress_for")

        text = "SELECT %(columns)s "\
            "FROM ALL_TABLES%(dblink)s "\
            "WHERE table_name = "+"'"+table_name+"' "

        if schema is not None:
            text += " AND owner =  "+"'"+schema+"' "
        text = text % {'dblink': dblink, 'columns': ", ".join(columns)}

        result = connection.execute(sql.text(text))

        enabled = dict(DISABLED=False, ENABLED=True)

        row = result.first()
        if row:
            if "compression" in row and enabled.get(row.compression, False):
                if "compress_for" in row:
                    options['xg_compress'] = row.compress_for
                else:
                    options['xg_compress'] = True

        return options

    @reflection.cache
    def get_columns(self, connection, table_name, schema=None, **kw):
        self.trace_process('XGDialect', 'get_columns', connection, table_name, schema, **kw)
        """


        """

        resolve_synonyms = kw.get('xg_resolve_synonyms', False)
        dblink = kw.get('dblink', '')
        info_cache = kw.get('info_cache')
        kind = kw.get('kind')
        (table_name, schema, dblink, synonym) = \
            self._prepare_reflection_args(connection, table_name, schema,
                                          resolve_synonyms, dblink,
                                          info_cache=info_cache)
        columns = []

        if kind == 'view':
            if schema is None:
                text = f"""select col_name  as column_name,type_name as data_type, SCALE,NULL as nullable, NULL as data_default  from all_view_columns where
                                view_id = (select view_id from all_views t where view_name = '{table_name}') order BY col_no;
                                    """
            else:
                text = f"""select col_name  as column_name,type_name as data_type, SCALE,NULL as nullable, NULL as data_default  from all_view_columns where
                            view_id = (select view_id from all_views t where view_name = '{table_name}' and schema_id = (select schema_id from all_schemas where schema_name = '{schema}')) order BY col_no;
                        """
        else:
            if schema is None:
                text = f"""select col_name  as column_name,type_name as data_type, SCALE,DECODE (NOT_NULL, TRUE, FALSE, TRUE) as nullable, def_val as data_default  from all_columns where
                    table_id = (select table_id from all_tables t where table_name = '{table_name}') order BY col_no;
                            """
            else:
                text = f"""select col_name  as column_name,type_name as data_type, SCALE,DECODE (NOT_NULL, TRUE, FALSE, TRUE) as nullable, def_val as data_default from all_columns where
                    table_id = (select table_id from all_tables t where table_name = '{table_name}' and schema_id = (select schema_id from all_schemas where schema_name = '{schema}')) order BY col_no;
                        """

        c = connection.execute(sql.text(text))

        for row in c:
            (colname, coltype, scale, nullable, default) = \
                ( row[0], row[1], row[2], row[3], row[4])

            if coltype in ('VARCHAR', 'CHAR'):
                if scale == -1:
                    coltype = self.ischema_names.get(coltype)
                else:
                    coltype = self.ischema_names.get(coltype)(scale)
            elif 'WITH TIME ZONE' in coltype:
                coltype = TIMESTAMP(timezone=True)
            elif coltype in ('NUMERIC', 'BIGINT'):
                continue
            else:
                try:
                    coltype = self.ischema_names[coltype]
                except KeyError:
                    util.warn("Did not recognize type '%s' of column '%s'" %
                              (coltype, colname))
                    coltype = sqltypes.NULLTYPE
            cdict = {
                'name': colname,
                'type': coltype,
                'nullable': nullable,
                'default': default,
                'autoincrement': 'auto',
            }
            if colname.lower() == colname:
                cdict['quote'] = True

            columns.append(cdict)
        return columns
    
    @reflection.cache
    def get_table_comment(
        self,
        connection,
        table_name,
        schema=None,
        resolve_synonyms=False,
        dblink="",
        **kw
    ):
        self.trace_process('XGDialect', 'get_table_comment', connection, table_name, schema, resolve_synonyms, dblink, **kw)
        
        info_cache = kw.get("info_cache")
        (table_name, schema, dblink, synonym) = self._prepare_reflection_args(
            connection,
            table_name,
            schema,
            resolve_synonyms,
            dblink,
            info_cache=info_cache,
        )

        if not schema:
            schema = self.default_schema_name

        COMMENT_SQL = """
            SELECT comments
            FROM all_tables
            WHERE table_name = :table_name AND schema_id = (select schema_id from all_schemas where schema_name = :schema_name and db_id = (select db_id from all_databases where db_name = current_database) );
        """

        c = connection.execute(
            sql.text(COMMENT_SQL).bindparams(table_name=table_name, schema_name=schema)
        )
        return {"text": c.scalar()}    

    @reflection.cache
    def get_indexes(self, connection, table_name, schema=None,
                    resolve_synonyms=False, dblink='', **kw):
        self.trace_process('XGDialect', 'get_indexes', 
                           connection, table_name, schema,
                           resolve_synonyms, dblink, **kw)

        info_cache = kw.get('info_cache')
        (table_name, schema, dblink, synonym) = \
            self._prepare_reflection_args(connection, table_name, schema,
                                          resolve_synonyms, dblink,
                                          info_cache=info_cache)
        indexes = []

        params = {'table_name': table_name}
        text = \
            "SELECT a.index_name, a.column_name, "\
            "\nb.index_type, b.uniqueness, b.compression, b.prefix_length "\
            "\nFROM ALL_IND_COLUMNS%(dblink)s a, "\
            "\nALL_INDEXES%(dblink)s b "\
            "\nWHERE "\
            "\na.index_name = b.index_name "\
            "\nAND a.table_owner = b.table_owner "\
            "\nAND a.table_name = b.table_name "\
            "\nAND a.table_name =  "+"'"+table_name+"' "

        if schema is not None:
            params['schema'] = schema
            text += "AND a.table_owner =  "+"'"+schema+"' "

        text += "ORDER BY a.index_name, a.column_position"

        text = text % {'dblink': dblink}

        q = sql.text(text)
        rp = connection.execute(q)
        indexes = []
        last_index_name = None
        pk_constraint = self.get_pk_constraint(
            connection, table_name, schema, resolve_synonyms=resolve_synonyms,
            dblink=dblink, info_cache=kw.get('info_cache'))
        pkeys = pk_constraint['constrained_columns']
        uniqueness = dict(NONUNIQUE=False, UNIQUE=True)
        enabled = dict(DISABLED=False, ENABLED=True)

        xg_sys_col = re.compile(r'SYS_NC\d+\$', re.IGNORECASE)

        def upper_name_set(names):
            return set([i.upper() for i in names])

        pk_names = upper_name_set(pkeys)

        def remove_if_primary_key(index):
            
            # don't include the primary key index
            if index is not None and \
               upper_name_set(index['column_names']) == pk_names:
                indexes.pop()

        index = None
        for rset in rp:
            if rset.index_name != last_index_name:
                remove_if_primary_key(index)
                index = dict(name=rset.index_name,
                             column_names=[], dialect_options={})
                indexes.append(index)
            index['unique'] = uniqueness.get(rset.uniqueness, False)

            if rset.index_type in ('BITMAP', 'FUNCTION-BASED BITMAP'):
                index['dialect_options']['xg_bitmap'] = True
            if enabled.get(rset.compression, False):
                index['dialect_options']['xg_compress'] = rset.prefix_length

            if not xg_sys_col.match(rset.column_name):
                index['column_names'].append(rset.column_name)
            last_index_name = rset.index_name
        remove_if_primary_key(index)
        return indexes

    @reflection.cache
    def _get_constraint_data(self, connection, table_name, schema=None,
                             dblink='', **kw):
        self.trace_process('XGDialect', '_get_constraint_data', connection, table_name, schema, dblink, **kw)


        text = \
            "SELECT"\
            "\nac.constraint_name,"\
            "\nac.constraint_type,"\
            "\nloc.column_name AS local_column,"\
            "\nrem.table_name AS remote_table,"\
            "\nrem.column_name AS remote_column,"\
            "\nrem.owner AS remote_owner,"\
            "\nloc.position as loc_pos,"\
            "\nrem.position as rem_pos"\
            "\nFROM all_constraints%(dblink)s ac,"\
            "\nall_cons_columns%(dblink)s loc,"\
            "\nall_cons_columns%(dblink)s rem"\
            "\nWHERE ac.table_name = "+"'"+table_name+"' "\
            "\nAND ac.constraint_type IN ('R','P','U')"

        if schema is not None:
            text += "\nAND ac.owner = "+"'"+schema+"' "

        text += \
            "\nAND ac.owner = loc.owner"\
            "\nAND ac.constraint_name = loc.constraint_name"\
            "\nAND ac.r_owner = rem.owner(+)"\
            "\nAND ac.r_constraint_name = rem.constraint_name(+)"\
            "\nAND (rem.position IS NULL or loc.position=rem.position)"\
            "\nORDER BY ac.constraint_name, loc.position"

        text = text % {'dblink': dblink}
        rp = connection.execute(sql.text(text))
        constraint_data = rp.fetchall()
        return constraint_data

    @reflection.cache
    def get_pk_constraint(self, connection, table_name, schema=None, **kw):
        self.trace_process('XGDialect', 'get_pk_constraint', connection, table_name, schema, **kw)
        
        resolve_synonyms = kw.get('xg_resolve_synonyms', False)
        dblink = kw.get('dblink', '')
        info_cache = kw.get('info_cache')

        (table_name, schema, dblink, synonym) = \
            self._prepare_reflection_args(connection, table_name, schema,
                                          resolve_synonyms, dblink,
                                          info_cache=info_cache)
        pkeys = []
        constraint_name = None
        constraint_data = self._get_constraint_data(
            connection, table_name, schema, dblink,
            info_cache=kw.get('info_cache'))

        for row in constraint_data:
            (cons_name, cons_type, local_column, remote_table, remote_column, remote_owner) = \
                row[0:2] + tuple([x for x in row[2:6]])
            if cons_type == 'P':
                if constraint_name is None:
                    constraint_name = cons_name
                pkeys.append(local_column)
        return {'constrained_columns': pkeys, 'name': constraint_name}

    @reflection.cache
    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        self.trace_process('XGDialect', 'get_foreign_keys', connection, table_name, schema, **kw)
        
        requested_schema = schema  # to check later on
        resolve_synonyms = kw.get('xg_resolve_synonyms', False)
        dblink = kw.get('dblink', '')
        info_cache = kw.get('info_cache')

        (table_name, schema, dblink, synonym) = \
            self._prepare_reflection_args(connection, table_name, schema,
                                          resolve_synonyms, dblink,
                                          info_cache=info_cache)

        constraint_data = self._get_constraint_data(
            connection, table_name, schema, dblink,
            info_cache=kw.get('info_cache'))

        def fkey_rec():
            return {
                'name': None,
                'constrained_columns': [],
                'referred_schema': None,
                'referred_table': None,
                'referred_columns': []
            }

        fkeys = util.defaultdict(fkey_rec)

        for row in constraint_data:
            (cons_name, cons_type, local_column, remote_table, remote_column, remote_owner) = \
                row[0:2] + tuple([x for x in row[2:6]])

            if cons_type == 'R':
                if remote_table is None:
                    # ticket 363
                    util.warn(
                        ("Got 'None' querying 'table_name' from "
                         "all_cons_columns%(dblink)s - does the user have "
                         "proper rights to the table?") % {'dblink': dblink})
                    continue

                rec = fkeys[cons_name]
                rec['name'] = cons_name
                local_cols, remote_cols = rec[
                    'constrained_columns'], rec['referred_columns']

                if not rec['referred_table']:
                    if resolve_synonyms:
                        ref_remote_name, ref_remote_owner, ref_dblink, ref_synonym = \
                            self._resolve_synonym(
                                connection,
                                desired_owner=self.denormalize_name(
                                    remote_owner),
                                desired_table=self.denormalize_name(
                                    remote_table)
                            )
                        if ref_synonym:
                            remote_table = ref_synonym
                            remote_owner = ref_remote_owner

                    rec['referred_table'] = remote_table

                    if requested_schema is not None or \
                       self.denormalize_name(remote_owner) != schema:
                        rec['referred_schema'] = remote_owner

                local_cols.append(local_column)
                remote_cols.append(remote_column)

        return list(fkeys.values())

    @reflection.cache
    def get_unique_constraints(self, connection, table_name, schema=None, **kw):
        self.trace_process('XGDialect', 'get_unique_constraints',
                           connection, table_name, schema, **kw)
        
        resolve_synonyms = kw.get('xg_resolve_synonyms', False)
        dblink = kw.get('dblink', '')
        info_cache = kw.get('info_cache')

        (table_name, schema, dblink, synonym) = \
            self._prepare_reflection_args(connection, table_name, schema,
                                          resolve_synonyms, dblink,
                                          info_cache=info_cache)
        #ukeys = []
        ucons = []
        #exist = False
        constraint_name = None
        constraint_data = self._get_constraint_data(
            connection, table_name, schema, dblink,
            info_cache=kw.get('info_cache'))

        for row in constraint_data:
            (cons_name, cons_type, local_column, remote_table, remote_column, remote_owner) = \
                row[0:2] + tuple([x for x in row[2:6]])
            if cons_type == 'U':
                
                constraint_name = cons_name
                
                exist = False
                for rcon in ucons:
                    if rcon['name'] == constraint_name:
                        rcon['column_names'].append(local_column)
                        exist = True
                        
                if not exist:
                    new_con = {}
                    ukeys = []
                    new_con['name'] = constraint_name
                    ukeys.append(local_column)
                    new_con['column_names'] = ukeys
                    ucons.append(new_con)
                 
                #if constraint_name is None:
                #    constraint_name = self.normalize_name(cons_name)
                #ukeys.append(local_column)
                #ucons.append({'column_names': ukeys, 'name': constraint_name})
        #return {'column_names': ukeys, 'name': constraint_name}
        return ucons
    
    @reflection.cache
    def get_view_definition(self, connection, view_name, schema=None,
                            resolve_synonyms=False, dblink='', **kw):
        self.trace_process('XGDialect', 'get_view_definition',
                           connection, view_name, schema,
                           resolve_synonyms, dblink, **kw)
        
        info_cache = kw.get('info_cache')
        (view_name, schema, dblink, synonym) = \
            self._prepare_reflection_args(connection, view_name, schema,
                                          resolve_synonyms, dblink,
                                          info_cache=info_cache)

        params = {'view_name': view_name}
        text = "SELECT text FROM all_views WHERE view_name=:view_name"

        if schema is not None:
            text += " AND owner = :schema"
            params['schema'] = schema

        rp = connection.execute(sql.text(text), **params).scalar()
        if rp:
            return rp
        else:
            return None
        
    @reflection.cache
    def get_check_constraints(
        self, connection, table_name, schema=None, include_all=False, **kw
    ):
        resolve_synonyms = kw.get("xg_resolve_synonyms", False)
        dblink = kw.get("dblink", "")
        info_cache = kw.get("info_cache")

        (table_name, schema, dblink, synonym) = self._prepare_reflection_args(
            connection,
            table_name,
            schema,
            resolve_synonyms,
            dblink,
            info_cache=info_cache,
        )

        constraint_data = self._get_constraint_data(
            connection,
            table_name,
            schema,
            dblink,
            info_cache=kw.get("info_cache"),
        )

        check_constraints = filter(lambda x: x[1] == "C", constraint_data)

        return [
            {"name": cons[0], "sqltext": cons[8]}
            for cons in check_constraints
            if include_all or not re.match(r"..+?. IS NOT NULL$", cons[8])
        ]    

