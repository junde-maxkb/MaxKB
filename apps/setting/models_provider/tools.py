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
from sqlalchemy import create_engine, inspect, Table, MetaData,select
from sqlalchemy.exc import SQLAlchemyError

from common.config.embedding_config import ModelManage
from setting.models import Model
from setting.models_provider import get_model
from django.utils.translation import gettext_lazy as _
from sqlalchemy import text


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
            return create_engine(uri, pool_pre_ping=True, connect_args={'connect_timeout': 5})
        elif db_params['db_type'] == 'oracle':
            sid_or_service = db_params.get('sid') or db_params.get('service_name')
            if not sid_or_service:
                raise ValueError("Oracle连接需要提供SID或Service Name")

            # 使用cx_Oracle驱动
            uri = f"oracle+cx_oracle://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/?service_name={sid_or_service}"
            return create_engine(uri, pool_pre_ping=True, connect_args={'connect_timeout': 5})

        else:
            raise ValueError(f"不支持的数据库类型: {db_params['db_type']}")

    @classmethod
    def test_connection(cls, db_params):
        try:
            engine = cls._get_engine(db_params)
            with engine.connect() as conn:
                return True
        except SQLAlchemyError as e:
            return False

    @classmethod
    def get_tables(cls, db_params):
        try:
            engine = cls._get_engine(db_params)
            inspector = inspect(engine)
            db_type = db_params['db_type']

            if db_type == 'oracle':
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT table_name FROM user_tables"))
                    tables = [row[0] for row in result]
                    return True, tables

            elif db_type == 'postgresql':
                schema = db_params.get('schema', 'public')
                return True, inspector.get_table_names(schema=schema)

            elif db_type == 'mysql':
                return True, inspector.get_table_names()

        except SQLAlchemyError as e:
            return False, str(e)

    @classmethod
    def get_columns(cls, db_params, table_name):
        try:
            engine = cls._get_engine(db_params)
            inspector = inspect(engine)
            db_type = db_params['db_type']
            columns = []
            comments = {}
            schema = db_params.get('schema')

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

            else:
                return True, []

        except SQLAlchemyError as e:
            return False, str(e)

    @classmethod
    def query_columns(cls, db_params, table_name, columns):
        """
        查询指定字段的所有数据
        :param db_params: 数据库连接参数
        :param table_name: 表名
        :param columns: 要查询的字段列表
        :return: JSON格式数据
        """
        try:
            engine = cls._get_engine(db_params)
            metadata = MetaData()
            db_type = db_params['db_type']

            if db_type == 'oracle':
                table_name = table_name.upper()
                columns = [col.upper() for col in columns]

            with engine.connect() as conn:
                table = Table(table_name, metadata, autoload_with=engine)

                valid_columns = []
                for col in columns:
                    col_name = col.upper() if db_type == 'oracle' else col
                    if col_name not in table.columns:
                        raise ValueError(f"字段 {col} 不存在于表 {table_name}")
                    valid_columns.append(table.columns[col_name])

                stmt = select(*valid_columns)

                result = conn.execute(stmt)

                data = [dict(zip(columns, row)) for row in result]

                return data

        except SQLAlchemyError as e:
            raise RuntimeError(f"数据库操作失败: {str(e)}")
        finally:
            # 确保关闭连接
            if engine:
                engine.dispose()