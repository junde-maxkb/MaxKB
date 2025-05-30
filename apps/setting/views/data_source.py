from rest_framework.views import APIView
from rest_framework.views import Request
from common.response import result
from rest_framework.decorators import action
from common.auth import TokenAuth, has_permissions
from setting.models.data_source import DataSourceConfig
from setting.models_provider.tools import DBConnector
from setting.serializers.data_source_serializers import DBConfigerializer, DBConnectionSerializer


class DataSourceView(APIView):
    authentication_classes = [TokenAuth]

    def get(self, request: Request):
        queryset = DataSourceConfig.objects.all().order_by('name')
        serializer = DBConfigerializer(queryset, many=True)
        return result.success(serializer.data)

    def post(self, request: Request):
        serializer = DBConfigerializer(data=request.data)
        return result.success(serializer.add_data_source())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        def put(self, request: Request, id: str):
            return result.success(DBConfigerializer.Operate(data={"id": id}).edit(request.data))

        def get(self, request: Request, id: str):
            queryset = DataSourceConfig.objects.filter(id=id).first()
            serializer = DBConfigerializer(queryset)
            return result.success(serializer.data)

        def delete(self, request: Request, id: str):
            return result.success(DBConfigerializer.Operate().delete(id, with_valid=False))


class DbOperateView(APIView):
    authentication_classes = [TokenAuth]

    def get(self, request: Request, id: str):
        data_source = DataSourceConfig.objects.filter(id=id).first()
        db_params = {
            "db_type": data_source.db_type,
            "user": data_source.username,
            "password": data_source.password,
            "host": data_source.host,
            "port": data_source.port,
            "dbname": data_source.database_name,
            "schema": data_source.extra_params.get('schema')
        }
        state, tables = DBConnector.get_tables(db_params)
        if state:
            return result.success(tables)
        return result.error(tables)

    @action(detail=False, methods=['post'])
    def post(self, request):
        serializer = DBConnectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data_source = serializer.validated_data
        db_params = {
            "db_type": data_source.get('db_type'),
            "user": data_source.get('username'),
            "password": data_source.get('password'),
            "host": data_source.get('host'),
            "port": data_source.get('port'),
            "dbname": data_source.get('database_name'),
            "schema": data_source.get('extra_params').get('schema')
        }
        state = DBConnector.test_connection(db_params)
        if state:
            return result.success(state)
        return result.error(state)

    class Operate(APIView):
        def get(self, request: Request, id: str, table_name: str):
            data_source = DataSourceConfig.objects.filter(id=id).first()
            success, data = DBConnector.get_columns({
                "db_type": data_source.db_type,
                "user": data_source.username,
                "password": data_source.password,
                "host": data_source.host,
                "port": data_source.port,
                "dbname": data_source.database_name,
                "schema": data_source.extra_params.get('schema'),
            }, table_name)
            return result.success(data)

        def post(self, request):
            serializer = DBConnectionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data_source = serializer.data
            db_params = {
                "db_type": data_source.get('db_type'),
                "user": data_source.get('username'),
                "password": data_source.get('password'),
                "host": data_source.get('host'),
                "port": data_source.get('port'),
                "dbname": data_source.get('database_name'),
            }
            state, schemas = DBConnector.get_schemas(db_params)
            return result.success(schemas)
