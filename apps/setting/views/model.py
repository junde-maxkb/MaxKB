# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： model.py
    @date：2023/11/2 13:55
    @desc:
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import PermissionConstants
from common.log.log import log
from common.response import result
from common.util.common import query_params_to_single_dict
from setting.models_provider.constants.model_provider_constants import ModelProvideConstants
from setting.serializers.provider_serializers import ProviderSerializer, ModelSerializer, \
    get_default_model_params_setting
from setting.swagger_api.provide_api import ProvideApi, ModelCreateApi, ModelQueryApi, ModelEditApi
from django.utils.translation import gettext_lazy as _

from setting.views.common import get_model_operation_object, get_edit_model_details
from setting.services.direct_model_service import DirectModelService


class Model(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Create model'),
                         operation_id=_('Create model'),
                         request_body=ModelCreateApi.get_request_body_api()
        , tags=[_('model')])
    @has_permissions(PermissionConstants.MODEL_CREATE)
    @log(menu='model', operate='Create model',
         get_operation_object=lambda r, k: {'name': r.data.get('name')},
         get_details=get_edit_model_details)
    def post(self, request: Request):
        return result.success(
            ModelSerializer.Create(data={**request.data, 'user_id': str(request.user.id)}).insert(request.user.id,
                                                                                                  with_valid=True))

    @action(methods=['PUT'], detail=False)
    @swagger_auto_schema(operation_summary=_('Download model, trial only with Ollama platform'),
                         operation_id=_('Download model, trial only with Ollama platform'),
                         request_body=ModelCreateApi.get_request_body_api()
        , tags=[_('model')])
    @has_permissions(PermissionConstants.MODEL_CREATE)
    def put(self, request: Request):
        return result.success(
            ModelSerializer.Create(data={**request.data, 'user_id': str(request.user.id)}).insert(request.user.id,
                                                                                                  with_valid=True))

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('Get model list'),
                         operation_id=_('Get model list'),
                         manual_parameters=ModelQueryApi.get_request_params_api()
        , tags=[_('model')])
    @has_permissions(PermissionConstants.MODEL_READ)
    def get(self, request: Request):
        return result.success(
            ModelSerializer.Query(
                data={**query_params_to_single_dict(request.query_params), 'user_id': request.user.id}).list(
                with_valid=True))

    class ModelMeta(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_(
            'Query model meta information, this interface does not carry authentication information'),
            operation_id=_(
                'Query model meta information, this interface does not carry authentication information'),
            tags=[_('model')])
        @has_permissions(PermissionConstants.MODEL_READ)
        def get(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).one_meta(with_valid=True))

    class PauseDownload(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Pause model download'),
                             operation_id=_('Pause model download'),
                             tags=[_('model')])
        @has_permissions(PermissionConstants.MODEL_CREATE)
        def put(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).pause_download())

    class ModelParamsForm(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get model parameter form'),
                             operation_id=_('Get model parameter form'),
                             manual_parameters=ProvideApi.ModelForm.get_request_params_api(),
                             tags=[_('model')])
        @has_permissions(PermissionConstants.MODEL_READ)
        def get(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.ModelParams(data={'id': model_id, 'user_id': request.user.id}).get_model_params())

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Save model parameter form'),
                             operation_id=_('Save model parameter form'),
                             manual_parameters=ProvideApi.ModelForm.get_request_params_api(),
                             tags=[_('model')])
        @has_permissions(PermissionConstants.MODEL_READ)
        @log(menu='model', operate='Save model parameter form',
             get_operation_object=lambda r, k: get_model_operation_object(k.get('model_id')))
        def put(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.ModelParamsForm(data={'id': model_id, 'user_id': request.user.id})
                .save_model_params_form(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Update model'),
                             operation_id=_('Update model'),
                             request_body=ModelEditApi.get_request_body_api()
            , tags=[_('model')])
        @has_permissions(PermissionConstants.MODEL_CREATE)
        @log(menu='model', operate='Update model',
             get_operation_object=lambda r, k: get_model_operation_object(k.get('model_id')),
             get_details=get_edit_model_details)
        def put(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).edit(request.data,
                                                                                                str(request.user.id)))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_('Delete model'),
                             operation_id=_('Delete model'),
                             responses=result.get_default_response()
            , tags=[_('model')])
        @has_permissions(PermissionConstants.MODEL_DELETE)
        @log(menu='model', operate='Delete model',
             get_operation_object=lambda r, k: get_model_operation_object(k.get('model_id')))
        def delete(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).delete())

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Query model details'),
                             operation_id=_('Query model details'),
                             tags=[_('model')])
        @has_permissions(PermissionConstants.MODEL_READ)
        def get(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).one(with_valid=True))

    class Chat(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Direct model chat (single-turn, no history)'),
                             operation_id=_('Direct model chat (single-turn, no history)'),
                             tags=[_('model')])
        @has_permissions(PermissionConstants.MODEL_READ)
        def post(self, request: Request, model_id: str):
            """
            直接调用指定 model_id 的大语言模型进行单轮对话。
            请求体支持：
            - message: string（与下方 messages 互斥，优先使用 messages）
            - system: string（可选，和 message 搭配使用）
            - messages: [{ role: 'system'|'user'|'assistant', content: string }]
            额外参数将透传至底层模型调用。
            返回：{ content: string, metadata: any }
            """
            body = request.data or {}
            messages = body.get('messages')
            if not messages:
                system = body.get('system')
                message = body.get('message') or ''
                messages = []
                if system:
                    messages.append({ 'role': 'system', 'content': system })
                messages.append({ 'role': 'user', 'content': message })

            # 透传其他参数（如温度、最大token、stream等）
            extra = { k: v for k, v in body.items() if k not in ('messages', 'message', 'system') }
            # 携带用户ID，便于鉴权与路由私有模型
            extra['user_id'] = request.user.id if hasattr(request, 'user') else None

            # 是否流式
            stream = bool(extra.pop('stream', False))
            if stream:
                gen = DirectModelService.stream(model_id, messages, **extra)
                from django.http import StreamingHttpResponse
                import json

                def sse():
                    for chunk in gen:
                        yield 'data: ' + json.dumps({'content': getattr(chunk, 'content', getattr(chunk, 'text', '')) or ''}, ensure_ascii=False) + '\n\n'
                    yield 'data: ' + json.dumps({'content': '', 'is_end': True}, ensure_ascii=False) + '\n\n'

                r = StreamingHttpResponse(streaming_content=sse(), content_type='text/event-stream;charset=utf-8')
                r['Cache-Control'] = 'no-cache'
                return r
            else:
                resp = DirectModelService.chat(model_id, messages, **extra)
                return result.success(resp)


class Provide(APIView):
    authentication_classes = [TokenAuth]

    class Exec(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Call the supplier function to obtain form data'),
                             operation_id=_('Call the supplier function to obtain form data'),
                             manual_parameters=ProvideApi.get_request_params_api(),
                             request_body=ProvideApi.get_request_body_api()
            , tags=[_('model')])
        @has_permissions(PermissionConstants.MODEL_READ)
        @log(menu='model', operate='Call the supplier function to obtain form data')
        def post(self, request: Request, provider: str, method: str):
            return result.success(
                ProviderSerializer(data={'provider': provider, 'method': method}).exec(request.data, with_valid=True))

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('Get a list of model suppliers'),
                         operation_id=_('Get a list of model suppliers')
        , tags=[_('model')])
    @has_permissions(PermissionConstants.MODEL_READ)
    def get(self, request: Request):
        model_type = request.query_params.get('model_type')
        if model_type:
            providers = []
            for key in ModelProvideConstants.__members__:
                if len([item for item in ModelProvideConstants[key].value.get_model_type_list() if
                        item['value'] == model_type]) > 0:
                    providers.append(ModelProvideConstants[key].value.get_model_provide_info().to_dict())
            return result.success(providers)
        return result.success(
            [ModelProvideConstants[key].value.get_model_provide_info().to_dict() for key in
             ModelProvideConstants.__members__])

    class ModelTypeList(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get a list of model types'),
                             operation_id=_('Get a list of model types'),
                             manual_parameters=ProvideApi.ModelTypeList.get_request_params_api(),
                             responses=result.get_api_array_response(ProvideApi.ModelTypeList.get_response_body_api())
            , tags=[_('model')])
        @has_permissions(PermissionConstants.MODEL_READ)
        def get(self, request: Request):
            provider = request.query_params.get('provider')
            return result.success(ModelProvideConstants[provider].value.get_model_type_list())

    class ModelList(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get the model creation form'),
                             operation_id=_('Get the model creation form'),
                             manual_parameters=ProvideApi.ModelList.get_request_params_api(),
                             responses=result.get_api_array_response(ProvideApi.ModelList.get_response_body_api())
            , tags=[_('model')]
                             )
        @has_permissions(PermissionConstants.MODEL_READ)
        def get(self, request: Request):
            provider = request.query_params.get('provider')
            model_type = request.query_params.get('model_type')

            return result.success(
                ModelProvideConstants[provider].value.get_model_list(
                    model_type))

    class ModelParamsForm(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get model default parameters'),
                             operation_id=_('Get the model creation form'),
                             manual_parameters=ProvideApi.ModelList.get_request_params_api(),
                             responses=result.get_api_array_response(ProvideApi.ModelList.get_response_body_api())
            , tags=[_('model')]
                             )
        @has_permissions(PermissionConstants.MODEL_READ)
        def get(self, request: Request):
            provider = request.query_params.get('provider')
            model_type = request.query_params.get('model_type')
            model_name = request.query_params.get('model_name')

            return result.success(get_default_model_params_setting(provider, model_type, model_name))

    class ModelForm(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get the model creation form'),
                             operation_id=_('Get the model creation form'),
                             manual_parameters=ProvideApi.ModelForm.get_request_params_api(),
                             tags=[_('model')])
        @has_permissions(PermissionConstants.MODEL_READ)
        def get(self, request: Request):
            provider = request.query_params.get('provider')
            model_type = request.query_params.get('model_type')
            model_name = request.query_params.get('model_name')
            return result.success(
                ModelProvideConstants[provider].value.get_model_credential(model_type, model_name).to_form_list())
