# coding=utf-8
"""
    @project: MaxKB
    @Author：guofengang
    @file： tools.py
    @date：2025/5/24 11:18
    @desc:
"""
from django.db import connection
from django.db.models import QuerySet
from sqlalchemy import create_engine, inspect, Table, MetaData, select
from sqlalchemy.exc import SQLAlchemyError

from common.config.embedding_config import ModelManage
from setting.models import Model
from setting.models_provider import get_model
from django.utils.translation import gettext_lazy as _
from sqlalchemy import text
from sqlalchemy.dialects import registry

# 检查Oracle驱动是否可用
try:
    import oracledb

    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False

try:
    import dmPython

    DM_AVAILABLE = True
except ImportError:
    DM_AVAILABLE = False


def get_model_by_id(_id, user_id):
    model = QuerySet(Model).filter(id=_id).first()
    # 手动关闭数据库连接
    connection.close()
    if model is None:
        raise Exception(_('Model does not exist'))
    if model.permission_type == 'PRIVATE' and str(model.user_id) != str(user_id):
        raise Exception(_('No permission to use this model') + f"{model.name}")
    return model


def get_model_instance_by_model_user_id(model_id, user_id, **kwargs):
    """
    获取模型实例,根据模型相关数据
    @param model_id:  模型id
    @param user_id:   用户id
    @return:          模型实例
    """
    model = get_model_by_id(model_id, user_id)
    return ModelManage.get_model(model_id, lambda _id: get_model(model, **kwargs))


class DBConnector:
    @staticmethod
    def _get_engine(db_params):
        if db_params['db_type'] == 'postgresql':
            uri = f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
            # 添加schema处理
            connect_args = {
                'options': f'-c search_path={db_params.get("schema", "public")}',
                'connect_timeout': 5
            }
            return create_engine(uri, connect_args=connect_args)
        elif db_params['db_type'] == 'mysql':
            uri = f"mysql+pymysql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
            # PyMySQL 使用正确的连接参数
            connect_args = {
                'connect_timeout': 5,
                'read_timeout': 30,
                'write_timeout': 30
            }
            return create_engine(uri, pool_pre_ping=True, connect_args=connect_args)
        elif db_params['db_type'] == 'oracle':
            if not ORACLE_AVAILABLE:
                raise ValueError("Oracle数据库支持需要安装oracledb驱动: pip install oracledb")

            sid_or_service = db_params.get('sid') or db_params.get('service_name')
            if not sid_or_service:
                raise ValueError("Oracle连接需要提供SID或Service Name")

            # 使用oracledb驱动
            if db_params.get('sid'):
                # SID连接方式
                uri = f"oracle+oracledb://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{sid_or_service}"
            else:
                # Service Name连接方式
                uri = f"oracle+oracledb://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/?service_name={sid_or_service}"

            # oracledb 连接配置 - 不使用 connect_args 中的超时参数
            # 超时参数通过 SQLAlchemy 引擎级别设置
            return create_engine(
                uri,
                pool_pre_ping=True,
                pool_timeout=30,  # 连接池超时
                pool_recycle=3600,  # 连接回收时间
                echo=False
            )

        elif db_params['db_type'] == 'dm':
            if not DM_AVAILABLE:
                raise ValueError("达梦数据库支持需要安装dmPython驱动: pip install dmPython")
            # 达梦数据库连接
            uri = f"dm+dmPython://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}"
            return create_engine(
                uri,
                pool_pre_ping=True,
                pool_timeout=30,  # 连接池超时
                pool_recycle=3600,  # 连接回收时间
                echo=False
            )
        elif db_params['db_type'] == 'xg':
            print(db_params)
            registry.register("xg", "xg.xgPython", "dialect")
            engine_url = f"xg://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
            return create_engine(
                engine_url,
                pool_pre_ping=True,
                pool_timeout=30,  # 连接池超时
                pool_recycle=3600,  # 连接回收时间
                echo=False
            )
        else:
            raise ValueError(f"不支持的数据库类型: {db_params['db_type']}")

    @classmethod
    def test_connection(cls, db_params):
        try:
            engine = cls._get_engine(db_params)
            with engine.connect() as conn:
                return True
        except Exception as e:
            # 记录详细错误信息用于调试
            print(f"数据库连接测试失败: {str(e)}")
            if "unexpected keyword argument" in str(e):
                print("提示: 检查数据库驱动版本和连接参数配置")
            return False

    @classmethod
    def get_tables(cls, db_params):
        try:
            engine = cls._get_engine(db_params)
            inspector = inspect(engine)
            db_type = db_params['db_type']

            if db_type == 'oracle':
                with engine.connect() as conn:
                    # 根据是否指定schema来决定查询策略
                    schema = db_params.get('schema')

                    if schema:
                        # 如果指定了schema，查询该schema下的表
                        print(f"Oracle: 查询指定schema '{schema}' 下的表")
                        result = conn.execute(text("""
                            SELECT table_name FROM all_tables 
                            WHERE owner = :schema_name
                            AND table_name NOT LIKE 'LOGMNR_%'
                            AND table_name NOT LIKE 'SYS_%'
                            AND table_name NOT LIKE 'APEX_%' 
                            AND table_name NOT LIKE 'FLOWS_%'
                            AND table_name NOT LIKE 'MVIEW$%'
                            AND table_name NOT LIKE 'SQLPLUS_%'
                            AND table_name NOT LIKE 'MDRS_%'
                            AND table_name NOT LIKE 'MDXT_%'
                            AND table_name NOT LIKE 'WRI$%'
                            AND table_name NOT LIKE 'PLAN_TABLE%'
                            AND table_name NOT LIKE '%$'
                            AND table_name NOT LIKE 'BIN$%'
                            AND table_name NOT LIKE 'DR$%'
                            AND table_name NOT IN ('DUAL')
                            ORDER BY table_name
                        """), {'schema_name': schema.upper()})
                    else:
                        # 如果没有指定schema，查询当前用户的表
                        print("Oracle: 查询当前用户的表")
                        result = conn.execute(text("""
                            SELECT table_name FROM user_tables 
                            WHERE table_name NOT LIKE 'LOGMNR_%'
                            AND table_name NOT LIKE 'SYS_%'
                            AND table_name NOT LIKE 'APEX_%' 
                            AND table_name NOT LIKE 'FLOWS_%'
                            AND table_name NOT LIKE 'MVIEW$%'
                            AND table_name NOT LIKE 'SQLPLUS_%'
                            AND table_name NOT LIKE 'MDRS_%'
                            AND table_name NOT LIKE 'MDXT_%'
                            AND table_name NOT LIKE 'WRI$%'
                            AND table_name NOT LIKE 'PLAN_TABLE%'
                            AND table_name NOT LIKE '%$'
                            AND table_name NOT LIKE 'BIN$%'
                            AND table_name NOT LIKE 'DR$%'
                            AND table_name NOT IN ('DUAL')
                            ORDER BY table_name
                        """))

                    tables = [row[0] for row in result]
                    print(f"Oracle: 找到 {len(tables)} 个表")
                    return True, tables

            elif db_type == 'postgresql':
                schema = db_params.get('schema', 'public')
                return True, inspector.get_table_names(schema=schema)

            elif db_type == 'mysql':
                return True, inspector.get_table_names()

            elif db_type == 'dm':
                with engine.connect() as conn:
                    schema = db_params.get('schema')
                    if schema:
                        target_schema = schema.upper()
                        result = conn.execute(text("""
                            SELECT table_name FROM all_tables 
                            WHERE owner = :schema 
                              AND table_name NOT LIKE 'SYS%'
                              AND table_name NOT LIKE 'DBA_%'
                              AND table_name NOT LIKE 'ALL_%'
                              AND table_name NOT LIKE 'USER_%'
                              AND table_name NOT LIKE 'V$%'
                              AND table_name NOT LIKE 'GV$%'
                              AND table_name NOT LIKE 'X$%'
                              AND owner NOT IN ('SYS', 'SYSTEM', 'SYSDBA')
                            ORDER BY table_name
                        """), {'schema': target_schema}).fetchall()
                        print(f"DM: 共找到 {result} 表 in schema {target_schema}")
                        tables = [row[0] for row in result]
                    else:
                        result = conn.execute(
                            text("""
                                SELECT table_name FROM user_tables 
                                WHERE table_name NOT LIKE 'SYS%'
                                AND table_name NOT LIKE 'DBA_%'
                                AND table_name NOT LIKE 'ALL_%'
                                AND table_name NOT LIKE 'USER_%'
                                AND table_name NOT LIKE 'V$%'
                                AND table_name NOT LIKE 'GV$%'
                                AND table_name NOT LIKE 'X$%'
                                ORDER BY table_name
                                            """)
                        ).fetchall()
                        tables = [row[0] for row in result]
                        print(f"DM: 共找到 {tables} 个表 in all user schemas")
                    return True, tables

            elif db_type == 'xg':
                with engine.connect() as conn:
                    schema = db_params.get('schema')
                    if schema:
                        target_schema = schema.upper()
                        result = conn.execute(
                            text(
                                """
                                SELECT t.table_name
                                FROM dba_tables t
                                JOIN dba_schemas s
                                  ON t.schema_id = s.schema_id
                                  AND t.db_id = s.db_id
                                WHERE s.schema_name = :schema
                                  AND t.table_name NOT LIKE 'SYS%'
                                  AND t.table_name NOT LIKE 'DBA_%'
                                  AND t.table_name NOT LIKE 'ALL_%'
                                  AND t.table_name NOT LIKE 'USER_%'
                                ORDER BY t.table_name
                                """
                            ),
                            {"schema": target_schema},
                        ).fetchall()
                        tables = [row[0] for row in result]
                        print(f"XG: 共找到 {len(tables)} 个表 in schema {target_schema}")
                    else:
                        result = conn.execute(
                            text(
                                """
                                SELECT table_name FROM user_tables 
                                WHERE table_name NOT LIKE 'SYS%'
                                  AND table_name NOT LIKE 'DBA_%'
                                  AND table_name NOT LIKE 'ALL_%'
                                  AND table_name NOT LIKE 'USER_%'
                                  AND table_name NOT LIKE 'V$%'
                                  AND table_name NOT LIKE 'GV$%'
                                  AND table_name NOT LIKE 'X$%'
                                ORDER BY table_name
                                """
                            )
                        ).fetchall()
                        tables = [row[0] for row in result]
                        print(f"XG: 共找到 {len(tables)} 个表 (当前用户)")
                    return True, tables
        except Exception as e:
            # 记录详细错误信息用于调试
            error_msg = str(e)
            print(f"获取表列表失败: {error_msg}")
            if "unexpected keyword argument" in error_msg:
                error_msg = f"数据库驱动参数错误: {error_msg}。请检查驱动版本和配置。"
            return False, error_msg

    @classmethod
    def get_columns(cls, db_params, table_name):
        try:
            engine = cls._get_engine(db_params)
            inspector = inspect(engine)
            db_type = db_params['db_type']
            columns = []
            comments = {}
            schema = db_params.get('schema')
            print(f"获取列信息调用: {db_params}, 表名: {table_name}, Schema: {schema}")
            if db_type == 'oracle':
                with engine.connect() as conn:
                    # 获取列信息
                    col_query = text(f"""
                                SELECT column_name, data_type, data_length, data_precision, data_scale, nullable
                                FROM all_tab_columns
                                WHERE table_name = :table_name
                                AND owner = :schema
                                ORDER BY column_id
                            """)
                    result = conn.execute(col_query, {
                        'table_name': table_name.upper(),
                        'schema': schema.upper() if schema else db_params['user'].upper()
                    })

                    # 获取列注释
                    comment_query = text("""
                                SELECT column_name, comments
                                FROM all_col_comments
                                WHERE table_name = :table_name
                                AND owner = :schema
                            """)
                    comment_result = conn.execute(comment_query, {
                        'table_name': table_name.upper(),
                        'schema': schema.upper() if schema else db_params['user'].upper()
                    })
                    comments = {row[0]: row[1] for row in comment_result}

                    # 构建列信息
                    for row in result:
                        col_info = {
                            'name': row[0],
                            'type': row[1],
                            'db_comment': comments.get(row[0], ''),
                            'verbose_name': row[0]  # Oracle没有verbose_name概念
                        }
                        columns.append(col_info)

            elif db_type == 'postgresql' and schema:
                columns = inspector.get_columns(table_name, schema=schema)
                comment_sql = text(f"""
                            SELECT a.attname, pg_catalog.col_description(a.attrelid, a.attnum)
                            FROM pg_catalog.pg_attribute a
                            WHERE a.attrelid = '{schema}.{table_name}'::regclass
                            AND a.attnum > 0
                        """)
                with engine.connect() as conn:
                    result = conn.execute(comment_sql)
                    comments = {row[0]: row[1] for row in result}

            elif db_type == 'mysql':
                columns = inspector.get_columns(table_name)
                comment_sql = text("""
                            SELECT COLUMN_NAME, COLUMN_COMMENT 
                            FROM INFORMATION_SCHEMA.COLUMNS 
                            WHERE TABLE_SCHEMA = :db 
                              AND TABLE_NAME = :table
                        """)
                with engine.connect() as conn:
                    result = conn.execute(
                        comment_sql,
                        {"db": db_params['dbname'], "table": table_name}
                    )
                    comments = {row[0]: row[1] for row in result}

            elif db_type == 'dm':
                with engine.connect() as conn:
                    current_user = conn.execute(text("SELECT USER FROM DUAL")).scalar()

                    res = conn.execute(text("""
                        SELECT SCH.NAME AS schema_name
                          FROM SYSOBJECTS SCH
                          JOIN DBA_USERS U ON SCH.PID = U.USER_ID
                         WHERE SCH.TYPE$ = 'SCH'
                           AND U.USERNAME = :user
                         ORDER BY SCH.NAME
                    """), {'user': current_user.upper()})
                    user_schemas = [row[0] for row in res]

                    found_schema = None
                    table_name_upper = table_name.upper()
                    for sch in user_schemas:
                        table_check = conn.execute(
                            text("SELECT COUNT(*) FROM all_tables WHERE owner = :schema AND table_name = :table"),
                            {"schema": sch, "table": table_name_upper}
                        ).scalar()
                        if table_check:
                            found_schema = sch
                            break
                    if not found_schema:
                        raise ValueError(f"找不到表 {table_name}，或者它不属于当前用户拥有的 schema。")

                    cols = conn.execute(
                        text("""
                            SELECT column_name, data_type, data_length 
                            FROM all_tab_columns 
                            WHERE owner = :schema AND table_name = :table
                            ORDER BY column_id
                        """),
                        {"schema": found_schema, "table": table_name_upper}
                    ).fetchall()
                    col_comments = conn.execute(
                        text("""
                            SELECT column_name, comments 
                            FROM all_col_comments 
                            WHERE owner = :schema AND table_name = :table
                        """),
                        {"schema": found_schema, "table": table_name_upper}
                    ).fetchall()
                    comment_map = {col: cm for col, cm in col_comments}
                    columns = []
                    for col_name, data_type, data_length in cols:
                        columns.append({
                            'name': col_name,
                            'type': f"{data_type}({data_length})" if data_length else data_type,
                            'db_comment': comment_map.get(col_name, ''),
                            'verbose_name': col_name
                        })
                    return True, columns

            elif db_type == 'xg':
                with engine.connect() as conn:
                    if schema:
                        result = conn.execute(
                            text("""
                                SELECT col_name, comments FROM 
                                dba_columns WHERE 
                                table_id = (
                                    SELECT t.table_id FROM dba_tables t
                                    JOIN dba_schemas s ON t.schema_id = s.schema_id AND t.db_id = s.db_id
                                    WHERE t.table_name = :table AND s.schema_name = :schema
                                )
                                """),
                            {"schema": schema.upper(), "table": table_name.upper()},
                        ).fetchall()
                    else:
                        result = conn.execute(
                            text("""
                                SELECT col_name, comments FROM
                                dba_columns WHERE 
                                table_id = (
                                    SELECT t.table_id FROM dba_tables t
                                    JOIN dba_schemas s ON t.schema_id = s.schema_id AND t.db_id = s.db_id
                                    WHERE t.table_name = :table
                                )
                                ORDER BY col_name
                                """),
                            {"table": table_name.upper()},
                        ).fetchall()

                    columns = []
                    for row in result:
                        col_name = row[0]
                        data_type = row[1] if len(row) > 1 else 'UNKNOWN'
                        comment = row[2] if len(row) > 2 else ''

                        columns.append({
                            'name': col_name,
                            'type': data_type,
                            'db_comment': comment or '',
                            'verbose_name': col_name
                        })

                    return True, columns

            model = cls._find_model(table_name)
            verbose_names = {
                field.name: field.verbose_name
                for field in model._meta.get_fields()
                if hasattr(field, 'verbose_name')
            } if model else {}

            # 构建结果
            data = [{
                "name": col['name'] if db_type != 'oracle' else col['name'],
                "type": str(col['type']) if db_type != 'oracle' else col['type'],
                "db_comment": col.get('db_comment', ''),
                "verbose_name": verbose_names.get(col['name'], col['name'])
            } for col in columns]

            return (True, data)

        except SQLAlchemyError as e:
            raise RuntimeError(f"数据库操作失败: {str(e)}")

    @staticmethod
    def _find_model(table_name):
        """自动查找匹配的Django模型"""
        from django.apps import apps
        for model in apps.get_models():
            if model._meta.db_table == table_name:
                return model
        return None

    @classmethod
    def get_schemas(cls, db_params):
        try:
            print(f"获取Schema调用: {db_params}")
            # 添加详细调试信息
            engine = cls._get_engine(db_params)
            db_type = db_params['db_type']

            # Oracle处理逻辑 - Oracle中的schema就是用户名
            if db_type == 'oracle':
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT username FROM all_users"))
                    schemas = [row[0] for row in result]
                    return True, schemas

            elif db_type == 'postgresql':
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT schema_name FROM information_schema.schemata"))
                    schemas = [row[0] for row in result]
                    system_schemas = {'pg_catalog', 'information_schema', 'pg_toast'}
                    return True, [s for s in schemas if s not in system_schemas]
            elif db_type == "dm":
                with engine.connect() as conn:
                    current_user = conn.execute(text("SELECT USER FROM DUAL")).scalar()
                    res = conn.execute(text("""
                        SELECT SCH.NAME AS schema_name
                          FROM SYSOBJECTS SCH
                          JOIN DBA_USERS U ON SCH.PID = U.USER_ID
                         WHERE SCH.TYPE$ = 'SCH'
                           AND U.USERNAME = :user
                         ORDER BY SCH.NAME
                    """), {'user': current_user.upper()})
                    schemas = [row[0] for row in res]
                    return True, schemas
            elif db_type == "xg":
                with engine.connect() as conn:
                    result = conn.execute(
                        text("SELECT schema_name FROM user_schemas ORDER BY schema_name")
                    )
                    schema_rows = result.fetchall()
                    target_schemas = [row[0] for row in schema_rows]
                    return True, target_schemas
            else:
                return True, []

        except Exception as e:
            # 记录详细错误信息用于调试
            error_msg = str(e)
            print(f"获取Schema失败: {error_msg}")
            if "unexpected keyword argument" in error_msg:
                error_msg = f"数据库驱动参数错误: {error_msg}。请检查驱动版本和配置。"
            return False, error_msg

    @classmethod
    def query_columns(cls, db_params, table_name, columns):
        """
        查询指定字段的所有数据
        :param db_params: 数据库连接参数
        :param table_name: 表名
        :param columns: 要查询的字段列表
        :return: JSON格式数据
        """
        engine = None
        try:
            engine = cls._get_engine(db_params)
            metadata = MetaData()
            db_type = db_params['db_type']

            # 添加详细调试信息
            print(f"{db_type} Debug: query_columns调用")
            print(f"  db_params: {db_params}")
            print(f"  table_name: {table_name}")
            print(f"  columns: {columns}")

            if db_type == 'oracle':
                table_name = table_name.upper()
                columns = [col.upper() for col in columns]

                # 双重检查：确保不访问Oracle系统表
                system_table_patterns = [
                    'LOGMNR_', 'SYS_', 'APEX_', 'FLOWS_', 'MVIEW$', 'SQLPLUS_',
                    'MDRS_', 'MDXT_', 'WRI$', 'PLAN_TABLE', 'BIN$', 'DR$'
                ]
                if (table_name.endswith('$') or
                        table_name == 'DUAL' or
                        any(table_name.startswith(pattern) for pattern in system_table_patterns)):
                    raise ValueError(f"表 {table_name} 是系统表，不允许访问。请选择业务表。")

            with engine.connect() as conn:
                # 检查表是否存在且可访问
                # Oracle专用：直接使用SQL查询，避免autoload问题
                if db_type == 'oracle':
                    schema = db_params.get('schema')
                    if schema:
                        print(f"Oracle: 直接SQL查询表 {table_name} (schema: {schema})")
                        # 构建完全限定的表名
                        qualified_table = f"{schema.upper()}.{table_name}"
                    else:
                        print(f"Oracle: 直接SQL查询表 {table_name} (当前用户schema)")
                        qualified_table = table_name

                    # 验证字段是否存在
                    print(f"Oracle: 验证字段 {columns}")
                    for col in columns:
                        col_upper = col.upper()
                        check_sql = text("""
                            SELECT COUNT(*) FROM all_tab_columns 
                            WHERE table_name = :table_name 
                            AND column_name = :column_name
                            AND owner = :owner
                        """)
                        result = conn.execute(check_sql, {
                            'table_name': table_name,
                            'column_name': col_upper,
                            'owner': schema.upper() if schema else db_params['user'].upper()
                        })
                        if result.fetchone()[0] == 0:
                            raise ValueError(f"字段 {col} 不存在于表 {qualified_table}")

                    # 构建查询SQL
                    column_list = ', '.join([f'"{col.upper()}"' for col in columns])
                    query_sql = text(f'SELECT {column_list} FROM {qualified_table}')
                    print(f"Oracle: 执行SQL: {query_sql}")

                    result = conn.execute(query_sql)
                    data = [dict(zip(columns, row)) for row in result]
                    print(f"Oracle: 查询成功，返回 {len(data)} 行数据")
                    return data

                if db_type == 'dm':
                    table_name_input = table_name
                    columns_input = columns
                    schema = db_params.get('schema')

                    current_user = conn.execute(text("SELECT USER FROM DUAL")).scalar()

                    if schema:
                        # 如果指定了schema，直接使用指定的schema
                        print(f"DM: 使用指定的schema: {schema}")
                        found_schema = schema.upper()

                        # 验证schema是否存在且用户有权限访问
                        schema_check = conn.execute(
                            text("""
                                SELECT COUNT(*) FROM SYSOBJECTS SCH
                                JOIN DBA_USERS U ON SCH.PID = U.USER_ID
                                WHERE SCH.TYPE$ = 'SCH' 
                                AND SCH.NAME = :schema
                                AND U.USERNAME = :user
                            """),
                            {'schema': found_schema, 'user': current_user.upper()}
                        ).scalar()

                        if schema_check == 0:
                            raise ValueError(f"Schema {schema} 不存在或用户 {current_user} 没有访问权限")

                        actual_table_name = None
                        table_candidates = [table_name_input, table_name_input.upper(), table_name_input.lower()]

                        for candidate_table in table_candidates:
                            table_check = conn.execute(
                                text("SELECT COUNT(*) FROM all_tables WHERE owner = :schema AND table_name = :table"),
                                {"schema": found_schema, "table": candidate_table}
                            ).scalar()
                            if table_check > 0:
                                actual_table_name = candidate_table
                                break
                        if not actual_table_name:
                            available_tables = conn.execute(
                                text("SELECT table_name FROM all_tables WHERE owner = :schema"),
                                {"schema": found_schema}
                            ).fetchall()
                            table_names = [row[0] for row in available_tables]
                            raise ValueError(
                                f"在schema {found_schema} 中未找到表: {table_name_input}。可用表: {table_names}")
                    else:
                        # 如果没有指定schema，搜索用户拥有的所有schema
                        print(f"DM: 未指定schema，搜索用户 {current_user} 拥有的所有schema")
                        res = conn.execute(text("""
                            SELECT SCH.NAME AS schema_name
                              FROM SYSOBJECTS SCH
                              JOIN DBA_USERS U ON SCH.PID = U.USER_ID
                             WHERE SCH.TYPE$ = 'SCH'
                               AND U.USERNAME = :user
                             ORDER BY SCH.NAME
                        """), {'user': current_user.upper()})
                        user_schemas = [row[0] for row in res]

                        print(f"DM: 用户 {current_user} 拥有的schemas: {user_schemas}")

                        # 查找表所在的schema
                        found_schema = None
                        actual_table_name = None
                        table_candidates = [table_name_input, table_name_input.upper(), table_name_input.lower()]

                        for candidate_table in table_candidates:
                            for sch in user_schemas:
                                table_check = conn.execute(
                                    text(
                                        "SELECT COUNT(*) FROM all_tables WHERE owner = :schema AND table_name = :table"),
                                    {"schema": sch, "table": candidate_table}
                                ).scalar()
                                if table_check > 0:
                                    found_schema = sch
                                    actual_table_name = candidate_table
                                    break
                            if found_schema:
                                break

                        if not found_schema:
                            available_tables = []
                            for sch in user_schemas:
                                tables = conn.execute(
                                    text("SELECT table_name FROM all_tables WHERE owner = :schema"),
                                    {"schema": sch}
                                ).fetchall()
                                for table in tables:
                                    available_tables.append(f"{sch}.{table[0]}")

                            raise ValueError(
                                f"达梦数据库未找到表: {table_name_input}。可用表: {available_tables[:10]}...")

                    print(f"DM: 找到表 {actual_table_name} 在schema {found_schema}")

                    columns_checked = []
                    for col in columns_input:
                        col_candidates = [col, col.upper(), col.lower()]
                        found_col = None
                        for candidate_col in col_candidates:
                            col_check = conn.execute(
                                text(
                                    "SELECT COUNT(*) FROM all_tab_columns WHERE owner = :schema AND table_name = :table AND column_name = :column"),
                                {"schema": found_schema, "table": actual_table_name, "column": candidate_col}
                            ).scalar()
                            if col_check > 0:
                                found_col = candidate_col
                                break

                        if not found_col:
                            actual_columns = conn.execute(
                                text(
                                    "SELECT column_name FROM all_tab_columns WHERE owner = :schema AND table_name = :table"),
                                {"schema": found_schema, "table": actual_table_name}
                            ).fetchall()
                            col_names = [row[0] for row in actual_columns]
                            raise ValueError(
                                f"达梦数据库表 {found_schema}.{actual_table_name} 中未找到字段: {col}。可用字段: {col_names}")

                        columns_checked.append(found_col)

                    print(f"DM: 验证字段成功: {columns_checked}")

                    # 构建查询SQL
                    column_list = ', '.join([f'"{col}"' for col in columns_checked])
                    qualified_table = f'{found_schema}.{actual_table_name}'
                    query_sql = text(f'SELECT {column_list} FROM {qualified_table}')

                    print(f"DM: 执行SQL: {query_sql}")
                    result = conn.execute(query_sql)
                    data = [dict(zip(columns_input, row)) for row in result]
                    print(f"DM: 查询成功，返回 {len(data)} 行数据")
                    print(f"DM: 查询成功，返回数据: {data[:5]}...")
                    return data
                if db_type == 'xg':
                    table_name_input = table_name
                    columns_input = columns
                    schema = db_params.get('schema')

                    if schema:
                        # 如果指定了schema，直接使用指定的schema
                        print(f"XG: 使用指定的schema: {schema}")
                        found_schema = schema.upper()

                        # 验证表是否存在
                        table_check = conn.execute(
                            text("""
                                SELECT COUNT(*) FROM dba_tables t
                                JOIN dba_schemas s ON t.schema_id = s.schema_id AND t.db_id = s.db_id
                                WHERE s.schema_name = :schema AND t.table_name = :table
                            """),
                            {"schema": found_schema, "table": table_name_input.upper()}
                        ).scalar()

                        if table_check == 0:
                            raise ValueError(f"XG数据库schema {found_schema} 中未找到表: {table_name_input}")

                        actual_table_name = table_name_input.upper()
                    else:
                        # 如果没有指定schema，查找表所在的schema
                        print(f"XG: 未指定schema，搜索表 {table_name_input}")

                        # 查找表所在的schema
                        schema_result = conn.execute(
                            text("""
                                SELECT s.schema_name FROM dba_tables t
                                JOIN dba_schemas s ON t.schema_id = s.schema_id AND t.db_id = s.db_id
                                WHERE t.table_name = :table
                            """),
                            {"table": table_name_input.upper()}
                        ).fetchone()

                        if not schema_result:
                            raise ValueError(f"XG数据库未找到表: {table_name_input}")

                        found_schema = schema_result[0]
                        actual_table_name = table_name_input.upper()

                    print(f"XG: 找到表 {actual_table_name} 在schema {found_schema}")

                    # 验证字段是否存在
                    columns_checked = []
                    for col in columns_input:
                        col_check = conn.execute(
                            text("""
                                SELECT COUNT(*) FROM dba_columns c
                                JOIN dba_tables t ON c.table_id = t.table_id
                                JOIN dba_schemas s ON t.schema_id = s.schema_id AND t.db_id = s.db_id
                                WHERE s.schema_name = :schema 
                                AND t.table_name = :table 
                                AND c.col_name = :column
                            """),
                            {"schema": found_schema, "table": actual_table_name, "column": col.upper()}
                        ).scalar()

                        if col_check == 0:
                            # 获取可用字段列表用于错误提示
                            available_cols = conn.execute(
                                text("""
                                    SELECT c.col_name FROM dba_columns c
                                    JOIN dba_tables t ON c.table_id = t.table_id
                                    JOIN dba_schemas s ON t.schema_id = s.schema_id AND t.db_id = s.db_id
                                    WHERE s.schema_name = :schema AND t.table_name = :table
                                    ORDER BY c.col_id
                                """),
                                {"schema": found_schema, "table": actual_table_name}
                            ).fetchall()
                            col_names = [row[0] for row in available_cols]
                            raise ValueError(
                                f"XG数据库表 {found_schema}.{actual_table_name} 中未找到字段: {col}。可用字段: {col_names}")

                        columns_checked.append(col.upper())

                    print(f"XG: 验证字段成功: {columns_checked}")

                    # 构建查询SQL
                    column_list = ', '.join([f'"{col}"' for col in columns_checked])
                    qualified_table = f'{found_schema}.{actual_table_name}'
                    query_sql = text(f'SELECT {column_list} FROM {qualified_table}')

                    print(f"XG: 执行SQL: {query_sql}")
                    result = conn.execute(query_sql)
                    data = [dict(zip(columns_input, row)) for row in result]
                    print(f"XG: 查询成功，返回 {len(data)} 行数据")
                    return data
                else:
                    # 非Oracle数据库使用原来的autoload方式
                    try:
                        table = Table(table_name, metadata, autoload_with=engine)
                    except Exception as table_error:
                        if "NoSuchTableError" in str(table_error) or "不存在" in str(table_error):
                            raise ValueError(f"表 {table_name} 不存在或没有访问权限。请检查表名和用户权限。")
                        else:
                            raise ValueError(f"无法访问表 {table_name}: {str(table_error)}")

                    valid_columns = []
                    for col in columns:
                        if col not in table.columns:
                            raise ValueError(f"字段 {col} 不存在于表 {table_name}")
                        valid_columns.append(table.columns[col])

                    stmt = select(*valid_columns)
                    result = conn.execute(stmt)
                    data = [dict(zip(columns, row)) for row in result]
                    return data

        except Exception as e:
            print(f"查询字段数据失败: {str(e)}")
            raise RuntimeError(f"数据库操作失败: {str(e)}")
        finally:
            # 确保关闭连接
            if engine:
                engine.dispose()
