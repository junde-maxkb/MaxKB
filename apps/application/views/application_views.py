# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： application_views.py
    @date：2023/10/27 14:56
    @desc:
"""

from django.core import cache
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _, gettext
from drf_yasg.utils import swagger_auto_schema
from langchain_core.prompts import PromptTemplate
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView
from django.db.models import Q

from application.serializers.application_serializers import ApplicationSerializer
from application.serializers.application_statistics_serializers import ApplicationStatisticsSerializer
from application.swagger_api.application_api import ApplicationApi
from application.swagger_api.application_statistics_api import ApplicationStatisticsApi
from application.views.common import get_application_operation_object
from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import CompareConstants, PermissionConstants, Permission, Group, Operate, \
    ViewPermission, RoleConstants
from common.exception.app_exception import AppAuthenticationFailed
from common.log.log import log
from common.response import result
from common.swagger_api.common_api import CommonApi
from common.util.common import query_params_to_single_dict
from dataset.serializers.dataset_serializers import DataSetSerializers

chat_cache = cache.caches['chat_cache']


class ApplicationStatistics(APIView):
    class CustomerCount(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary=_("User Statistics"),
                             operation_id=_("User Statistics"),
                             tags=[_("Application/Statistics")],
                             manual_parameters=ApplicationStatisticsApi.get_request_params_api(),
                             responses=result.get_api_response(
                                 ApplicationStatisticsApi.CustomerCount.get_response_body_api())
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationStatisticsSerializer(data={'application_id': application_id,
                                                      'start_time': request.query_params.get(
                                                          'start_time'),
                                                      'end_time': request.query_params.get(
                                                          'end_time')
                                                      }).get_customer_count())

    class CustomerCountTrend(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary=_("User demographic trends"),
                             operation_id=_("User demographic trends"),
                             tags=[_("Application/Statistics")],
                             manual_parameters=ApplicationStatisticsApi.get_request_params_api(),
                             responses=result.get_api_array_response(
                                 ApplicationStatisticsApi.CustomerCountTrend.get_response_body_api()))
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationStatisticsSerializer(data={'application_id': application_id,
                                                      'start_time': request.query_params.get(
                                                          'start_time'),
                                                      'end_time': request.query_params.get(
                                                          'end_time')
                                                      }).get_customer_count_trend())

    class ChatRecordAggregate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary=_("Conversation statistics"),
                             operation_id=_("Conversation statistics"),
                             tags=[_("Application/Statistics")],
                             manual_parameters=ApplicationStatisticsApi.get_request_params_api(),
                             responses=result.get_api_response(
                                 ApplicationStatisticsApi.ChatRecordAggregate.get_response_body_api())
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationStatisticsSerializer(data={'application_id': application_id,
                                                      'start_time': request.query_params.get(
                                                          'start_time'),
                                                      'end_time': request.query_params.get(
                                                          'end_time')
                                                      }).get_chat_record_aggregate())

    class ChatRecordAggregateTrend(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary=_("Dialogue-related statistical trends"),
                             operation_id=_("Dialogue-related statistical trends"),
                             tags=[_("Application/Statistics")],
                             manual_parameters=ApplicationStatisticsApi.get_request_params_api(),
                             responses=result.get_api_array_response(
                                 ApplicationStatisticsApi.ChatRecordAggregate.get_response_body_api())
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationStatisticsSerializer(data={'application_id': application_id,
                                                      'start_time': request.query_params.get(
                                                          'start_time'),
                                                      'end_time': request.query_params.get(
                                                          'end_time')
                                                      }).get_chat_record_aggregate_trend())


class Application(APIView):
    authentication_classes = [TokenAuth]

    class EditIcon(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_("Modify application icon"),
                             operation_id=_("Modify application icon"),
                             tags=[_('Application')],
                             manual_parameters=ApplicationApi.EditApplicationIcon.get_request_params_api(),
                             request_body=ApplicationApi.Operate.get_request_body_api())
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND), PermissionConstants.APPLICATION_EDIT,
            compare=CompareConstants.AND)
        @log(menu='Application', operate="Modify application icon",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
        def put(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.IconOperate(
                    data={'application_id': application_id, 'user_id': request.user.id,
                          'image': request.FILES.get('file')}).edit(request.data))

    class Import(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @action(methods="POST", detail=False)
        @swagger_auto_schema(operation_summary=_("Import Application"), operation_id=_("Import Application"),
                             manual_parameters=ApplicationApi.Import.get_request_params_api(),
                             tags=[_("Application")]
                             )
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        @log(menu='Application', operate="Import Application")
        def post(self, request: Request):
            return result.success(ApplicationSerializer.Import(
                data={'user_id': request.user.id, 'file': request.FILES.get('file')}).import_())

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary=_("Export Application"), operation_id=_("Export Application"),
                             manual_parameters=ApplicationApi.Export.get_request_params_api(),
                             tags=[_("Application")]
                             )
        @has_permissions(lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('application_id')))
        @log(menu='Application', operate="Export Application",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
        def get(self, request: Request, application_id: str):
            return ApplicationSerializer.Operate(
                data={'application_id': application_id, 'user_id': request.user.id}).export()

    class Embed(APIView):
        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary=_("Get embedded js"),
                             operation_id=_("Get embedded js"),
                             tags=[_("Application")],
                             manual_parameters=ApplicationApi.ApiKey.get_request_params_api())
        def get(self, request: Request):
            return ApplicationSerializer.Embed(
                data={'protocol': request.query_params.get('protocol'), 'token': request.query_params.get('token'),
                      'host': request.query_params.get('host'), }).get_embed(params=request.query_params)

    class Model(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary=_("Get a list of models"),
                             operation_id=_("Get a list of models"),
                             tags=[_("Application")],
                             manual_parameters=ApplicationApi.Model.get_request_params_api())
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.Operate(
                    data={'application_id': application_id,
                          'user_id': request.user.id}).list_model(request.query_params.get('model_type')))

    class ModelParamsForm(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get model parameter form"),
                             operation_id=_("Get model parameter form"),
                             tags=[_("Application")])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str, model_id: str):
            return result.success(
                ApplicationSerializer.Operate(
                    data={'application_id': application_id,
                          'user_id': request.user.id}).get_model_params_form(model_id))

    class FunctionLib(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary=_("Get a list of function libraries"),
                             operation_id=_("Get a list of function libraries"),
                             tags=[_("Application")])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.Operate(
                    data={'application_id': application_id,
                          'user_id': request.user.id}).list_function_lib())

        class Operate(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=["GET"], detail=False)
            @swagger_auto_schema(operation_summary=_("Get library details"),
                                 operation_id=_("Get library details"),
                                 tags=[_("Application")],
                                 )
            @has_permissions(ViewPermission(
                [RoleConstants.ADMIN, RoleConstants.USER],
                [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                dynamic_tag=keywords.get('application_id'))],
                compare=CompareConstants.AND))
            def get(self, request: Request, application_id: str, function_lib_id: str):
                return result.success(
                    ApplicationSerializer.Operate(
                        data={'application_id': application_id,
                              'user_id': request.user.id}).get_function_lib(function_lib_id))

    class Application(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get the list of apps created by the current user"),
                             operation_id=_("Get the list of apps created by the current user"),
                             tags=[_("Application/Chat")])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.Operate(
                    data={'application_id': application_id,
                          'user_id': request.user.id}).application_list())

        class Operate(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=["GET"], detail=False)
            @swagger_auto_schema(operation_summary=_("Get application data"),
                                 operation_id=_("Get application data"),
                                 tags=[_("Application")],
                                 )
            @has_permissions(ViewPermission(
                [RoleConstants.ADMIN, RoleConstants.USER],
                [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                dynamic_tag=keywords.get('application_id'))],
                compare=CompareConstants.AND))
            def get(self, request: Request, application_id: str, app_id: str):
                return result.success(
                    ApplicationSerializer.Operate(
                        data={'application_id': application_id,
                              'user_id': request.user.id}).get_application(app_id))

    class Profile(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get application related information"),
                             operation_id=_("Get application related information"),
                             tags=[_("Application/Chat")])
        def get(self, request: Request):
            if 'application_id' in request.auth.keywords:
                return result.success(ApplicationSerializer.Operate(
                    data={'application_id': request.auth.keywords.get('application_id'),
                          'user_id': request.user.id}).profile())
            raise AppAuthenticationFailed(401, "身份异常")

    class ApplicationKey(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_("Add ApiKey"),
                             operation_id=_("Add ApiKey"),
                             tags=[_('Application/API_KEY')],
                             manual_parameters=ApplicationApi.ApiKey.get_request_params_api())
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        @log(menu='Application', operate="Add ApiKey",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
        def post(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.ApplicationKeySerializer(
                    data={'application_id': application_id, 'user_id': request.user.id}).generate())

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get the application API_KEY list"),
                             operation_id=_("Get the application API_KEY list"),
                             tags=[_('Application/API_KEY')],
                             manual_parameters=ApplicationApi.ApiKey.get_request_params_api()
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(ApplicationSerializer.ApplicationKeySerializer(
                data={'application_id': application_id, 'user_id': request.user.id}).list())

        class Operate(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['PUT'], detail=False)
            @swagger_auto_schema(operation_summary=_("Modify application API_KEY"),
                                 operation_id=_("Modify application API_KEY"),
                                 tags=[_('Application/API_KEY')],
                                 manual_parameters=ApplicationApi.ApiKey.Operate.get_request_params_api(),
                                 request_body=ApplicationApi.ApiKey.Operate.get_request_body_api())
            @has_permissions(ViewPermission(
                [RoleConstants.ADMIN, RoleConstants.USER],
                [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                                dynamic_tag=keywords.get('application_id'))],
                compare=CompareConstants.AND), PermissionConstants.APPLICATION_EDIT,
                compare=CompareConstants.AND)
            @log(menu='Application', operate="Modify application API_KEY",
                 get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
            def put(self, request: Request, application_id: str, api_key_id: str):
                return result.success(
                    ApplicationSerializer.ApplicationKeySerializer.Operate(
                        data={'application_id': application_id, 'user_id': request.user.id,
                              'api_key_id': api_key_id}).edit(request.data))

            @action(methods=['DELETE'], detail=False)
            @swagger_auto_schema(operation_summary=_("Delete Application API_KEY"),
                                 operation_id=_("Delete Application API_KEY"),
                                 tags=[_('Application/API_KEY')],
                                 manual_parameters=ApplicationApi.ApiKey.Operate.get_request_params_api())
            @has_permissions(ViewPermission(
                [RoleConstants.ADMIN, RoleConstants.USER],
                [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                                dynamic_tag=keywords.get('application_id'))],
                compare=CompareConstants.AND), PermissionConstants.APPLICATION_DELETE,
                compare=CompareConstants.AND)
            @log(menu='Application', operate="Delete Application API_KEY",
                 get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
            def delete(self, request: Request, application_id: str, api_key_id: str):
                return result.success(
                    ApplicationSerializer.ApplicationKeySerializer.Operate(
                        data={'application_id': application_id, 'user_id': request.user.id,
                              'api_key_id': api_key_id}).delete())

    class AccessToken(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_("Modify Application AccessToken"),
                             operation_id=_("Modify Application AccessToken"),
                             tags=[_('Application/Public Access')],
                             manual_parameters=ApplicationApi.AccessToken.get_request_params_api(),
                             request_body=ApplicationApi.AccessToken.get_request_body_api())
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        @log(menu='Application', operate="Modify Application AccessToken",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
        def put(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.AccessTokenSerializer(data={'application_id': application_id}).edit(
                    request.data))

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get the application AccessToken information"),
                             operation_id=_("Get the application AccessToken information"),
                             manual_parameters=ApplicationApi.AccessToken.get_request_params_api(),
                             tags=[_('Application/Public Access')],
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.AccessTokenSerializer(data={'application_id': application_id}).one())

    class Authentication(APIView):
        @action(methods=['OPTIONS'], detail=False)
        def options(self, request, *args, **kwargs):
            return HttpResponse(
                headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true",
                         "Access-Control-Allow-Methods": "POST",
                         "Access-Control-Allow-Headers": "Origin,Content-Type,Cookie,Accept,Token"}, )

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_("Application Certification"),
                             operation_id=_("Application Certification"),
                             request_body=ApplicationApi.Authentication.get_request_body_api(),
                             tags=[_("Application/Certification")],
                             security=[])
        def post(self, request: Request):
            return result.success(
                ApplicationSerializer.Authentication(data={'access_token': request.data.get("access_token"),
                                                           'authentication_value': request.data.get(
                                                               'authentication_value')}).auth(
                    request),
                headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true",
                         "Access-Control-Allow-Methods": "POST",
                         "Access-Control-Allow-Headers": "Origin,Content-Type,Cookie,Accept,Token"}
            )

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_("Create an application"),
                         operation_id=_("Create an application"),
                         request_body=ApplicationApi.Create.get_request_body_api(),
                         tags=[_('Application')])
    @has_permissions(PermissionConstants.APPLICATION_CREATE, compare=CompareConstants.AND)
    @log(menu='Application', operate="Create an application",
         get_operation_object=lambda r, k: {'name': r.data.get('name')})
    def post(self, request: Request):
        return result.success(ApplicationSerializer.Create(data={'user_id': request.user.id}).insert(request.data))

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_("Get the application list"),
                         operation_id=_("Get the application list"),
                         manual_parameters=ApplicationApi.Query.get_request_params_api(),
                         responses=result.get_api_array_response(ApplicationApi.get_response_body_api()),
                         tags=[_('Application')])
    @has_permissions(PermissionConstants.APPLICATION_READ, compare=CompareConstants.AND)
    def get(self, request: Request):
        return result.success(
            ApplicationSerializer.Query(
                data={**query_params_to_single_dict(request.query_params), 'user_id': request.user.id}).list())

    class HitTest(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary=_("Hit Test List"), operation_id=_("Hit Test List"),
                             manual_parameters=CommonApi.HitTestApi.get_request_params_api(),
                             responses=result.get_api_array_response(CommonApi.HitTestApi.get_response_body_api()),
                             tags=[_("Application")])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_ACCESS_TOKEN,
             RoleConstants.APPLICATION_KEY],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.HitTest(data={'id': application_id, 'user_id': request.user.id,
                                                    "query_text": request.query_params.get("query_text"),
                                                    "top_number": request.query_params.get("top_number"),
                                                    'similarity': request.query_params.get('similarity'),
                                                    'search_mode': request.query_params.get(
                                                        'search_mode')}).hit_test(
                ))

    class Publish(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_("Publishing an application"),
                             operation_id=_("Publishing an application"),
                             manual_parameters=ApplicationApi.Operate.get_request_params_api(),
                             request_body=ApplicationApi.Publish.get_request_body_api(),
                             responses=result.get_default_response(),
                             tags=[_('Application')])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        @log(menu='Application', operate="Publishing an application",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
        def put(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.Operate(
                    data={'application_id': application_id, 'user_id': request.user.id}).publish(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_("Deleting application"),
                             operation_id=_("Deleting application"),
                             manual_parameters=ApplicationApi.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Application')])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND),
            lambda r, k: Permission(group=Group.APPLICATION, operate=Operate.DELETE,
                                    dynamic_tag=k.get('application_id')), compare=CompareConstants.AND)
        @log(menu='Application', operate="Deleting application",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
        def delete(self, request: Request, application_id: str):
            return result.success(ApplicationSerializer.Operate(
                data={'application_id': application_id, 'user_id': request.user.id}).delete(
                with_valid=True))

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_("Modify the application"),
                             operation_id=_("Modify the application"),
                             manual_parameters=ApplicationApi.Operate.get_request_params_api(),
                             request_body=ApplicationApi.Edit.get_request_body_api(),
                             responses=result.get_api_array_response(ApplicationApi.get_response_body_api()),
                             tags=[_('Application')])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        @log(menu='Application', operate="Modify the application",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
        def put(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.Operate(
                    data={'application_id': application_id, 'user_id': request.user.id}).edit(
                    request.data))

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get application details"),
                             operation_id=_("Get application details"),
                             manual_parameters=ApplicationApi.Operate.get_request_params_api(),
                             responses=result.get_api_array_response(ApplicationApi.get_response_body_api()),
                             tags=[_('Application')])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_ACCESS_TOKEN,
             RoleConstants.APPLICATION_KEY],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(ApplicationSerializer.Operate(
                data={'application_id': application_id, 'user_id': request.user.id}).one())

    class ListApplicationDataSet(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get the knowledge base available to the current application"),
                             operation_id=_("Get the knowledge base available to the current application"),
                             manual_parameters=ApplicationApi.Operate.get_request_params_api(),
                             responses=result.get_api_array_response(
                                 DataSetSerializers.Query.get_response_body_api()),
                             tags=[_('Application')])
        @has_permissions(ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                                        [lambda r, keywords: Permission(group=Group.APPLICATION,
                                                                        operate=Operate.USE,
                                                                        dynamic_tag=keywords.get(
                                                                            'application_id'))],
                                        compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            return result.success(ApplicationSerializer.Operate(
                data={'application_id': application_id, 'user_id': request.user.id}).list_dataset())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get the application list by page"),
                             operation_id=_("Get the application list by page"),
                             manual_parameters=result.get_page_request_params(
                                 ApplicationApi.Query.get_request_params_api()),
                             responses=result.get_page_api_response(ApplicationApi.get_response_body_api()),
                             tags=[_('Application')])
        @has_permissions(PermissionConstants.APPLICATION_READ, compare=CompareConstants.AND)
        def get(self, request: Request, current_page: int, page_size: int):
            return result.success(
                ApplicationSerializer.Query(
                    data={**query_params_to_single_dict(request.query_params), 'user_id': request.user.id}).page(
                    current_page, page_size))

    class SpeechToText(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @has_permissions(
            ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_ACCESS_TOKEN],
                           [lambda r, keywords: Permission(group=Group.APPLICATION,
                                                           operate=Operate.USE,
                                                           dynamic_tag=keywords.get(
                                                               'application_id'))],
                           compare=CompareConstants.AND))
        def post(self, request: Request, application_id: str):
            return result.success(
                ApplicationSerializer.Operate(data={'application_id': application_id, 'user_id': request.user.id})
                .speech_to_text(request.FILES.getlist('file')[0]))

    class TextToSpeech(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_("text to speech"),
                             operation_id=_("text to speech"),
                             manual_parameters=ApplicationApi.TextToSpeech.get_request_params_api(),
                             request_body=ApplicationApi.TextToSpeech.get_request_body_api(),
                             responses=result.get_default_response(),
                             tags=[_('Application')])
        @has_permissions(
            ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_ACCESS_TOKEN],
                           [lambda r, keywords: Permission(group=Group.APPLICATION,
                                                           operate=Operate.USE,
                                                           dynamic_tag=keywords.get(
                                                               'application_id'))],
                           compare=CompareConstants.AND))
        def post(self, request: Request, application_id: str):
            byte_data = ApplicationSerializer.Operate(
                data={'application_id': application_id, 'user_id': request.user.id}).text_to_speech(
                request.data.get('text'))
            return HttpResponse(byte_data, status=200, headers={'Content-Type': 'audio/mp3',
                                                                'Content-Disposition': 'attachment; filename="abc.mp3"'})

    class PlayDemoText(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @has_permissions(
            ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_ACCESS_TOKEN],
                           [lambda r, keywords: Permission(group=Group.APPLICATION,
                                                           operate=Operate.USE,
                                                           dynamic_tag=keywords.get(
                                                               'application_id'))],
                           compare=CompareConstants.AND))
        @log(menu='Application', operate="trial listening",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
        def post(self, request: Request, application_id: str):
            byte_data = ApplicationSerializer.Operate(
                data={'application_id': application_id, 'user_id': request.user.id}).play_demo_text(request.data)
            return HttpResponse(byte_data, status=200, headers={'Content-Type': 'audio/mp3',
                                                                'Content-Disposition': 'attachment; filename="abc.mp3"'})

    class McpServers(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @has_permissions(PermissionConstants.APPLICATION_READ, compare=CompareConstants.AND)
        def get(self, request: Request):
            return result.success(ApplicationSerializer.McpServers(
                data={'mcp_servers': request.query_params.get('mcp_servers')}).get_mcp_servers())

    class ApplicationMembers(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary=_('获取应用团队成员及其权限'),
                             operation_id=_('获取应用团队成员及其权限'),
                             manual_parameters=ApplicationApi.Operate.get_request_params_api(),
                             responses=result.get_api_response({
                                 'type': 'object',
                                 'properties': {
                                     'application_id': {'type': 'string'},
                                     'members': {
                                         'type': 'array',
                                         'items': {
                                             'type': 'object',
                                             'properties': {
                                                 'user_id': {'type': 'string'},
                                                 'username': {'type': 'string'},
                                                 'permission': {'type': 'string'}
                                             }
                                         }
                                     }
                                 }
                             }),
                             tags=[_('Application')])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, application_id: str):
            from setting.models.team_management import TeamMember, TeamMemberPermission
            from users.models import User
            from application.models.application import ApplicationShare

            # 获取需要忽略的用户ID列表
            ignore_user_ids = []
            team_members = TeamMember.objects.filter(team_id=request.user.id)
            for member in team_members:
                ignore_user_ids.append(member.user_id)
            ignore_user_ids.append(request.user.id)

            # 查询应用所有者ID
            application_share = ApplicationShare.objects.filter(
                application_id_id=application_id,
                shared_with_type='USER'
            ).exclude(
                shared_with_id__in=ignore_user_ids
            ).select_related('application_id')
            
            application_share_team = ApplicationShare.objects.filter(
                application_id_id=application_id,
                shared_with_type='TEAM'
            ).select_related('application_id')
            
            # 获取每个成员对当前应用的权限
            members_with_permissions = []
            for share in application_share:
                user = User.objects.get(id=share.shared_with_id)
                
                members_with_permissions.append({
                    'user_id': str(share.shared_with_id),
                    'type': 'USER',
                    'username': user.username,
                    'permission': share.permission if share.permission else 'NONE'
                })
                
            for share in application_share_team:
                Team = Team.objects.get(id=share.shared_with_id)
                
                members_with_permissions.append({
                    'user_id': str(share.shared_with_id),
                    'type': 'TEAM',
                    'username': Team.name,
                    'permission': share.permission if share.permission else 'NONE'
                })
                
            return result.success({
                'application_id': application_id,
                'members': members_with_permissions
            })

    class PutMemberPermissions(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["PUT"], detail=False)
        @swagger_auto_schema(operation_summary=_('更新应用分享权限'),
                             operation_id=_('更新应用分享权限'),
                             manual_parameters=ApplicationApi.Operate.get_request_params_api(),
                             request_body={
                                 'type': 'object',
                                 'properties': {
                                     'user_id': {'type': 'string', 'description': '用户ID'},
                                     'permission': {'type': 'string', 'description': '权限类型'},
                                     'share_with_type': {'type': 'string', 'description': '分享类型(USER/TEAM)'}
                                 },
                                 'required': ['user_id', 'permission', 'share_with_type']
                             },
                             responses=result.get_default_response(),
                             tags=[_('Application')])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND))
        @log(menu='Application', operate="更新应用分享权限",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
        def put(self, request: Request, application_id: str):
            from application.models.application import ApplicationShare, Application
            from django.utils import timezone
            
            user_id = request.data.get('user_id')
            permission = request.data.get('permission') if request.data.get('permission') else 'NONE'
            share_with_type = request.data.get('share_with_type')
            
            # 检查应用是否存在
            application = Application.objects.filter(id=application_id).first()
            if not application:
                return result.error(_('应用不存在'))
            
            if share_with_type == "USER":
                # 查找或创建分享记录
                share_record, created = ApplicationShare.objects.get_or_create(
                    application_id_id=application.id,
                    shared_with_type='USER',
                    shared_with_id=user_id,
                    defaults={'permission': permission}
                )
                # 如果记录已存在但权限不同，更新权限
                if not created and share_record.permission != permission:
                    share_record.permission = permission
                    share_record.save()
                    
            else:  # 团队类型
                # 假设user_id是团队ID
                team_id = user_id
                # 查找或创建团队分享记录
                share_record, created = ApplicationShare.objects.get_or_create(
                    application_id_id=application.id,
                    shared_with_type='TEAM',
                    shared_with_id=team_id,
                    defaults={'permission': permission}
                )
                # 如果记录已存在但权限不同，更新权限
                if not created and share_record.permission != permission:
                    share_record.permission = permission
                    share_record.save()
            
            return result.success({'message': '权限更新成功'})

    class ShareToMePage(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @has_permissions(PermissionConstants.APPLICATION_READ, compare=CompareConstants.AND)
        def get(self, request: Request, current_page, page_size):
            from setting.models.team_management import TeamMember
            from users.models import User
            from application.models.application import ApplicationShare
            
            # 从查询参数中获取分页信息
            current_page = int(request.query_params.get('current_page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # 1. 获取共享给我的应用ID列表及权限
            user_teams = TeamMember.objects.filter(Q(user_id=request.user.id) | Q(team_id=request.user.id)).values_list('team_id', flat=True)
            
            # 分别获取团队共享和用户共享的应用，并预先加载关联
            team_shared_applications = ApplicationShare.objects.filter(
                shared_with_type='TEAM',
                shared_with_id__in=[str(team_id) for team_id in user_teams]
            ).exclude(permission='NONE').select_related('application_id')
            
            user_shared_applications = ApplicationShare.objects.filter(
                shared_with_type='USER',
                shared_with_id=str(request.user.id)
            ).exclude(permission='NONE').select_related('application_id')
            
            # 合并两个查询集
            shared_applications = list(team_shared_applications) + list(user_shared_applications)

            # 如果没有共享的应用，直接返回空结果
            if not shared_applications:
                return result.success({
                    'records': [],
                    'total': 0,
                    'page': current_page,
                    'page_size': page_size
                })
            
            # 2. 构建查询参数
            query_params = {
                'name': request.query_params.get('name') or None,
                'desc': request.query_params.get("desc") or None,
                'user_id': str(request.user.id),
                'application_ids': [str(share.application_id_id) for share in shared_applications]
            }
            
            # 3. 使用Query获取应用列表
            d = ApplicationSerializer.SharePageQuery(data=query_params)
            d.is_valid()
            result_data = d.page(current_page, page_size)
            
            # 4. 为每个应用添加权限信息和创建人信息
            permission_map = {str(share.application_id_id): share.permission for share in shared_applications}
            
            # 获取所有应用的创建人信息
            creator_ids = [item['user_id'] for item in result_data['list']]
            creators = {str(user.id): user.username for user in User.objects.filter(id__in=creator_ids)}
            
            for item in result_data['list']:
                item['permission'] = permission_map.get(item['id'], 'NONE')
                item['creator_name'] = creators.get(str(item['user_id']), '')
            
            # 5. 修改返回数据结构，将list改为records
            return result.success({
                'records': result_data['list'],
                'total': result_data['total'],
                'page': result_data['page'],
                'page_size': result_data['page_size']
            })

    class ExitShare(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["PUT"], detail=False)
        @swagger_auto_schema(operation_summary=_('退出共享应用'),
                             operation_id=_('退出共享应用'),
                             manual_parameters=ApplicationApi.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Application')])
        def put(self, request: Request, application_id: str):
            from setting.models.team_management import TeamMember
            from application.models.application import ApplicationShare

            # 获取用户所在的团队
            user_teams = TeamMember.objects.filter(user_id=request.user.id).values_list('team_id', flat=True)
            
            # 检查团队共享
            team_share = ApplicationShare.objects.filter(
                application_id_id=application_id,
                shared_with_type='TEAM',
                shared_with_id__in=[str(team_id) for team_id in user_teams]
            ).exclude(permission='NONE').exists()
            
            # 检查个人共享
            user_share = ApplicationShare.objects.filter(
                application_id_id=application_id,
                shared_with_type='USER',
                shared_with_id=str(request.user.id)
            ).exclude(permission='NONE').exists()
            
            # 如果只有团队共享，不允许退出
            if team_share and not user_share:
                return result.error(_('该应用是通过团队共享的，无法退出'))
            
            # 如果有个人共享，将个人权限设置为NONE
            if user_share:
                ApplicationShare.objects.filter(
                    application_id_id=application_id,
                    shared_with_type='USER',
                    shared_with_id=str(request.user.id)
                ).update(permission='NONE')
            
            return result.success({'message': '成功退出共享应用'})
