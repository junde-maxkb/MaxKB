# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： user.py
    @date：2023/9/4 10:57
    @desc:
"""
import json
import secrets

import jwt
from django.core import cache, signing
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth.authenticate import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.authentication_type import AuthenticationType
from common.constants.permission_constants import PermissionConstants, CompareConstants, ViewPermission, RoleConstants
from common.log.log import log
from common.response import result
from common.util.common import encryption
from setting.serializers.system_setting import SystemSettingSerializer
from smartdoc import settings
from smartdoc.settings import JWT_AUTH
from users.serializers.user_serializers import RegisterSerializer, LoginSerializer, CheckCodeSerializer, \
    RePasswordSerializer, \
    SendEmailSerializer, UserProfile, UserSerializer, UserManageSerializer, UserInstanceSerializer, SystemSerializer, \
    SwitchLanguageSerializer, ChatHistorySerializer, ChatMessageSerializer
from users.views.common import get_user_operation_object, get_re_password_details
import requests
from django.shortcuts import redirect

user_cache = cache.caches['user_cache']
token_cache = cache.caches['token_cache']


class Profile(APIView):
    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_("Get MaxKB related information"),
                         operation_id=_("Get MaxKB related information"),
                         responses=result.get_api_response(SystemSerializer.get_response_body_api()),
                         tags=[_('System parameters')])
    def get(self, request: Request):
        return result.success(SystemSerializer.get_profile())


class User(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_("Get current user information"),
                         operation_id=_("Get current user information"),
                         responses=result.get_api_response(UserProfile.get_response_body_api()),
                         tags=[])
    @has_permissions(PermissionConstants.USER_READ)
    def get(self, request: Request):
        return result.success(UserProfile.get_user_profile(request.user))

    class Query(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get user list"),
                             operation_id=_("Get user list"),
                             manual_parameters=UserSerializer.Query.get_request_params_api(),
                             responses=result.get_api_array_response(UserSerializer.Query.get_response_body_api()),
                             tags=[_("User management")])
        @has_permissions(PermissionConstants.USER_READ)
        def get(self, request: Request):
            return result.success(
                UserSerializer.Query(data={'email_or_username': request.query_params.get('email_or_username')}).list())


class SwitchUserLanguageView(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_("Switch Language"),
                         operation_id=_("Switch Language"),
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             required=['language'],
                             properties={
                                 'language': openapi.Schema(type=openapi.TYPE_STRING, title=_("language"),
                                                            description=_("language")),
                             }
                         ),
                         responses=RePasswordSerializer().get_response_body_api(),
                         tags=[_("User management")])
    @log(menu='User management', operate='Switch Language',
         get_operation_object=lambda r, k: {'name': r.user.username})
    def post(self, request: Request):
        data = {**request.data, 'user_id': request.user.id}
        return result.success(SwitchLanguageSerializer(data=data).switch())


class ResetCurrentUserPasswordView(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_("Modify current user password"),
                         operation_id=_("Modify current user password"),
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             required=['email', 'code', "password", 're_password'],
                             properties={
                                 'code': openapi.Schema(type=openapi.TYPE_STRING, title=_("Verification code"),
                                                        description=_("Verification code")),
                                 'password': openapi.Schema(type=openapi.TYPE_STRING, title=_("Password"),
                                                            description=_("Password")),
                                 're_password': openapi.Schema(type=openapi.TYPE_STRING, title=_("Password"),
                                                               description=_("Password"))
                             }
                         ),
                         responses=RePasswordSerializer().get_response_body_api(),
                         tags=[_("User management")])
    @log(menu='User management', operate='Modify current user password',
         get_operation_object=lambda r, k: {'name': r.user.username},
         get_details=get_re_password_details)
    def post(self, request: Request):
        data = {'email': request.user.email}
        data.update(request.data)
        serializer_obj = RePasswordSerializer(data=data)
        if serializer_obj.reset_password():
            token_cache.delete(request.META.get('HTTP_AUTHORIZATION'))
            return result.success(True)
        return result.error(_("Failed to change password"))


class SendEmailToCurrentUserView(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @permission_classes((AllowAny,))
    @swagger_auto_schema(operation_summary=_("Send email to current user"),
                         operation_id=_("Send email to current user"),
                         responses=SendEmailSerializer().get_response_body_api(),
                         tags=[_("User management")])
    @log(menu='User management', operate='Send email to current user',
         get_operation_object=lambda r, k: {'name': r.user.username})
    def post(self, request: Request):
        serializer_obj = SendEmailSerializer(data={'email': request.user.email, 'type': "reset_password"})
        if serializer_obj.is_valid(raise_exception=True):
            return result.success(serializer_obj.send())


class Logout(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @permission_classes((AllowAny,))
    @swagger_auto_schema(operation_summary=_("Sign out"),
                         operation_id=_("Sign out"),
                         responses=SendEmailSerializer().get_response_body_api(),
                         tags=[_("User management")])
    @log(menu='User management', operate='Sign out',
         get_operation_object=lambda r, k: {'name': r.user.username})
    def post(self, request: Request):
        token_cache.delete(request.META.get('HTTP_AUTHORIZATION'))
        return result.success(True)


def _get_details(request):
    path = request.path
    body = request.data
    query = request.query_params
    return {
        'path': path,
        'body': {**body, 'password': encryption(body.get('password', ''))},
        'query': query
    }


class Login(APIView):

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_("Log in"),
                         operation_id=_("Log in"),
                         request_body=LoginSerializer().get_request_body_api(),
                         responses=LoginSerializer().get_response_body_api(),
                         security=[],
                         tags=[_("User management")])
    @log(menu='User management', operate='Log in', get_user=lambda r: {'username': r.data.get('username', None)},
         get_details=_get_details,
         get_operation_object=lambda r, k: {'name': r.data.get('username')})
    def post(self, request: Request):
        login_request = LoginSerializer(data=request.data)
        # 校验请求参数
        user = login_request.is_valid(raise_exception=True)
        token = login_request.get_user_token()
        token_cache.set(token, user, timeout=JWT_AUTH['JWT_EXPIRATION_DELTA'])
        return result.success(token)


class Register(APIView):

    @action(methods=['POST'], detail=False)
    @permission_classes((AllowAny,))
    @swagger_auto_schema(operation_summary=_("User registration"),
                         operation_id=_("User registration"),
                         request_body=RegisterSerializer().get_request_body_api(),
                         responses=RegisterSerializer().get_response_body_api(),
                         security=[],
                         tags=[_("User management")])
    @log(menu='User management', operate='User registration',
         get_operation_object=lambda r, k: {'name': r.data.get('username', None)},
         get_user=lambda r: {'user_name': r.data.get('username', None)})
    def post(self, request: Request):
        serializer_obj = RegisterSerializer(data=request.data)
        if serializer_obj.is_valid(raise_exception=True):
            serializer_obj.save()
            return result.success(_("Registration successful"))


class RePasswordView(APIView):

    @action(methods=['POST'], detail=False)
    @permission_classes((AllowAny,))
    @swagger_auto_schema(operation_summary=_("Change password"),
                         operation_id=_("Change password"),
                         request_body=RePasswordSerializer().get_request_body_api(),
                         responses=RePasswordSerializer().get_response_body_api(),
                         security=[],
                         tags=[_("User management")])
    @log(menu='User management', operate='Change password',
         get_operation_object=lambda r, k: {'name': r.data.get('email', None)},
         get_user=lambda r: {'user_name': None, 'email': r.data.get('email', None)},
         get_details=get_re_password_details)
    def post(self, request: Request):
        serializer_obj = RePasswordSerializer(data=request.data)
        return result.success(serializer_obj.reset_password())


class CheckCode(APIView):

    @action(methods=['POST'], detail=False)
    @permission_classes((AllowAny,))
    @swagger_auto_schema(operation_summary=_("Check whether the verification code is correct"),
                         operation_id=_("Check whether the verification code is correct"),
                         request_body=CheckCodeSerializer().get_request_body_api(),
                         responses=CheckCodeSerializer().get_response_body_api(),
                         security=[],
                         tags=[_("User management")])
    @log(menu='User management', operate='Check whether the verification code is correct',
         get_operation_object=lambda r, k: {'name': r.data.get('email', None)},
         get_user=lambda r: {'user_name': None, 'email': r.data.get('email', None)})
    def post(self, request: Request):
        return result.success(CheckCodeSerializer(data=request.data).is_valid(raise_exception=True))


class SendEmail(APIView):

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_("Send email"),
                         operation_id=_("Send email"),
                         request_body=SendEmailSerializer().get_request_body_api(),
                         responses=SendEmailSerializer().get_response_body_api(),
                         security=[],
                         tags=[_("User management")])
    @log(menu='User management', operate='Send email',
         get_operation_object=lambda r, k: {'name': r.data.get('email', None)},
         get_user=lambda r: {'user_name': None, 'email': r.data.get('email', None)})
    def post(self, request: Request):
        serializer_obj = SendEmailSerializer(data=request.data)
        if serializer_obj.is_valid(raise_exception=True):
            return result.success(serializer_obj.send())


class UserManage(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_("Add user"),
                         operation_id=_("Add user"),
                         request_body=UserManageSerializer.UserInstance.get_request_body_api(),
                         responses=result.get_api_response(UserInstanceSerializer.get_response_body_api()),
                         tags=[_("User management")]
                         )
    @has_permissions(ViewPermission(
        [RoleConstants.ADMIN],
        [PermissionConstants.USER_READ],
        compare=CompareConstants.AND))
    @log(menu='User management', operate='Add user',
         get_operation_object=lambda r, k: {'name': r.data.get('username', None)})
    def post(self, request: Request):
        return result.success(UserManageSerializer().save(request.data))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get user paginated list"),
                             operation_id=_("Get user paginated list"),
                             tags=[_("User management")],
                             manual_parameters=UserManageSerializer.Query.get_request_params_api(),
                             responses=result.get_page_api_response(UserInstanceSerializer.get_response_body_api()),
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN],
            [PermissionConstants.USER_READ],
            compare=CompareConstants.AND))
        def get(self, request: Request, current_page, page_size):
            d = UserManageSerializer.Query(
                data={'email_or_username': request.query_params.get('email_or_username', None),
                      'user_id': str(request.user.id)})
            return result.success(d.page(current_page, page_size))

    class RePassword(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_("Change password"),
                             operation_id=_("Change password"),
                             manual_parameters=UserInstanceSerializer.get_request_params_api(),
                             request_body=UserManageSerializer.RePasswordInstance.get_request_body_api(),
                             responses=result.get_default_response(),
                             tags=[_("User management")])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN],
            [PermissionConstants.USER_READ],
            compare=CompareConstants.AND))
        @log(menu='User management', operate='Change password',
             get_operation_object=lambda r, k: get_user_operation_object(k.get('user_id')),
             get_details=get_re_password_details)
        def put(self, request: Request, user_id):
            return result.success(
                UserManageSerializer.Operate(data={'id': user_id}).re_password(request.data, with_valid=True))

    class SetAdminManage(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_("Change password"),
                             operation_id=_("Change password"),
                             manual_parameters=UserInstanceSerializer.get_request_params_api(),
                             request_body=UserManageSerializer.RePasswordInstance.get_request_body_api(),
                             responses=result.get_default_response(),
                             tags=[_("User management")])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN],
            [PermissionConstants.USER_READ],
            compare=CompareConstants.AND))
        def put(self, request: Request, user_id):
            operate_user_id = request.user.id
            return result.success(
                UserManageSerializer.Operate(data={'id': user_id}).set_admin(request.data, operate_user_id,
                                                                             with_valid=True))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_("Delete user"),
                             operation_id=_("Delete user"),
                             manual_parameters=UserInstanceSerializer.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_("User management")])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN],
            [PermissionConstants.USER_READ],
            compare=CompareConstants.AND))
        @log(menu='User management', operate='Delete user',
             get_operation_object=lambda r, k: get_user_operation_object(k.get('user_id')))
        def delete(self, request: Request, user_id):
            return result.success(UserManageSerializer.Operate(data={'id': user_id}).delete(with_valid=True))

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get user information"),
                             operation_id=_("Get user information"),
                             manual_parameters=UserInstanceSerializer.get_request_params_api(),
                             responses=result.get_api_response(UserInstanceSerializer.get_response_body_api()),
                             tags=[_("User management")]
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN],
            [PermissionConstants.USER_READ],
            compare=CompareConstants.AND))
        def get(self, request: Request, user_id):
            return result.success(UserManageSerializer.Operate(data={'id': user_id}).one(with_valid=True))

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_("Update user information"),
                             operation_id=_("Update user information"),
                             manual_parameters=UserInstanceSerializer.get_request_params_api(),
                             request_body=UserManageSerializer.UserEditInstance.get_request_body_api(),
                             responses=result.get_api_response(UserInstanceSerializer.get_response_body_api()),
                             tags=[_("User management")]
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN],
            [PermissionConstants.USER_READ],
            compare=CompareConstants.AND))
        @log(menu='User management', operate='Update user information',
             get_operation_object=lambda r, k: get_user_operation_object(k.get('user_id')))
        def put(self, request: Request, user_id):
            return result.success(
                UserManageSerializer.Operate(data={'id': user_id}).edit(request.data, with_valid=True))


class UserListView(APIView):
    authentication_classes = [TokenAuth]

    @swagger_auto_schema(operation_summary=_("Get user list by type"),
                         operation_id=_("Get user list by type"),
                         manual_parameters=UserSerializer.Query.get_request_params_api(),
                         responses=result.get_api_array_response(UserSerializer.Query.get_response_body_api()),
                         tags=[_("User management")])
    @has_permissions(PermissionConstants.USER_READ)
    def get(self, request: Request, type):
        return result.success(UserSerializer().listByType(type, request.user.id))


class AuthConnect(APIView):
    def get(self, request):
        """
        生成GitHub授权URL并跳转
        """
        # 生成随机state防止CSRF
        state = secrets.token_urlsafe(16)
        request.session['oauth_state'] = state  # 存储到session
        oauth = SystemSettingSerializer.LoginAuthSerializer.one()
        params = {
            'client_id': oauth.get('client_id') if oauth.get('client_id') else settings.base.OAUTH2_CLIENT_ID,
            'redirect_uri': oauth.get('callback_url') if oauth.get(
                'callback_url') else settings.base.OAUTH2_REDIRECT_URI,
            'scope': oauth.get('connect_range') if oauth.get('connect_range') else 'user_info',  # 按需申请权限
            'state': state,
            'response_type': 'code'
        }
        auth_url = f"{oauth.get('authorized_url') if oauth.get('authorized_url') else settings.base.OAUTH2_AUTHORIZE_URI}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        return result.success(auth_url)


class OauthCallbackView(APIView):
    def get(self, request):
        """处理GitHub回调"""
        # 1. 验证state参数（防止CSRF）
        state = request.session.get('oauth_state', None)
        if 'state' not in request.GET or request.GET['state'] != state:
            return result.error(_("Invalid state'"))

        # 2. 获取临时code
        code = request.GET.get('code')
        if not code:
            return result.error(_("Authorization failed: code missing"))
        oauth = SystemSettingSerializer.LoginAuthSerializer.one()
        # 3. 用code换取access_token
        token_data = {
            'grant_type': "authorization_code",
            'client_id': oauth.get('client_id') if oauth.get('client_id') else settings.base.OAUTH2_CLIENT_ID,
            'client_secret': oauth.get('client_secret') if oauth.get(
                'client_secret') else settings.base.OAUTH2_CLIENT_SECRET,
            'code': code,
            'redirect_uri': oauth.get('callback_url') if oauth.get(
                'callback_url') else settings.base.OAUTH2_REDIRECT_URI
        }
        headers = {'Accept': 'application/json'}
        response = requests.post(oauth.get('token_url') if oauth.get('token_url') else settings.base.OAUTH2_TOKEN_URI,
                                 data=token_data, headers=headers)

        if response.status_code != 200:
            return result.error(_("Failed to get access token"))
        access_token = response.json().get('access_token')
        if not access_token:
            return result.error(_("Access token missing"))
        # 4. 使用access_token获取用户信息
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(oauth.get('user_url') if oauth.get('user_url') else settings.base.OAUTH2_USER_URL,
                                     headers=headers)
        user_data = user_response.json()

        user = UserSerializer.get_user_by_username(user_data.get('name'))
        if not user:
            return result.error(_("User not have permission to use"))

        token = signing.dumps({'username': user.username,
                               'id': str(user.id),
                               'email': user.email,
                               'type': AuthenticationType.USER.value})

        token_cache.set(token, user, timeout=JWT_AUTH['JWT_EXPIRATION_DELTA'])
        return redirect(f"{settings.base.MAXKB_HOME_URL}?token={token}")


class SSOLoginCallbackView(APIView):
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return result.error("缺少code")

        # 1. 用 code 换 id_token
        token_url = f"{settings.SSO_CONFIG['sso_base']}/oauth2/token"
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.SSO_CONFIG['redirect_uri'],
            'client_id': settings.SSO_CONFIG['client_id'],
            'client_secret': settings.SSO_CONFIG['client_secret'],
            'scope': 'openid',
        }
        token_resp = requests.post(token_url, data=token_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if token_resp.status_code != 200:
            return result.error("认证失败")

        token_json = token_resp.json()
        id_token = token_json.get('id_token')
        if not id_token:
            return result.error("认证失败，未返回认证信息")

        # 2. 解析 id_token（正式环境要校验签名！）
        try:
            payload = jwt.decode(id_token, options={"verify_signature": False}, algorithms=["RS256"])
        except jwt.PyJWTError as e:
            return result.error("认证信息解析失败")

        name = payload.get('name', '')
        email = payload.get('email')
        account = payload.get('account')

        if not email:
            if account:
                email = f"{account}@example.com"
            else:
                return result.error("认证信息中缺少邮箱")

        from users.models.user import User as UserModel
        # 3. 创建或获取用户
        user, created = QuerySet(UserModel).get_or_create(
            email=email,
            defaults={
                'username': name,
                'email': email,
                'nick_name': name,
                'role': 'USER',
                'source': 'SSO'
            }
        )

        # 4. 签发自己的 JWT
        token = signing.dumps({
            'username': user.username,
            'id': str(user.id),
            'type': AuthenticationType.USER.value
        })
        token_cache.set(token, user, timeout=JWT_AUTH['JWT_EXPIRATION_DELTA'])
        return result.success(token)


class ChatHistoryView(APIView):
    authentication_classes = [TokenAuth]

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get chat history paginated list"),
                             operation_id=_("Get chat history paginated list"),
                             tags=[_("User management")],
                             manual_parameters=ChatHistorySerializer.Query.get_request_params_api(),
                             responses=result.get_page_api_response(ChatHistorySerializer.Query.get_response_body_api()),
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN],
            [PermissionConstants.USER_READ],
            compare=CompareConstants.AND))
        def get(self, request: Request, user_id, current_page, page_size):
            keyword = request.query_params.get('keyword', None)
            d = ChatHistorySerializer.Query(
                data={'user_id': user_id, 'keyword': keyword})
            return result.success(d.page(current_page, page_size))

    class List(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get chat history list"),
                             operation_id=_("Get chat history list"),
                             tags=[_("User management")],
                             manual_parameters=ChatHistorySerializer.Query.get_request_params_api(),
                             responses=result.get_api_array_response(ChatHistorySerializer.Query.get_response_body_api()),
                             )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN],
            [PermissionConstants.USER_READ],
            compare=CompareConstants.AND))
        def get(self, request: Request, user_id):
            d = ChatHistorySerializer.Query(
                data={'user_id': user_id})
            return result.success(d.list())

    class Save(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_("Save chat history"),
                             operation_id=_("Save chat history"),
                             tags=[_("User management")],
                             request_body=ChatHistorySerializer.Instance.get_request_body_api(),
                             responses=result.get_api_response(ChatHistorySerializer.Instance.get_response_body_api()),
                             )
        def post(self, request: Request):
            d = ChatHistorySerializer.Instance(data=request.data)
            return result.success(d.save())


class ChatMessageView(APIView):
    authentication_classes = [TokenAuth]

    class Save(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_("Save chat message"),
                             operation_id=_("Save chat message"),
                             tags=[_("User management")],
                             request_body=ChatMessageSerializer.Instance.get_request_body_api(),
                             responses=result.get_api_response(ChatMessageSerializer.Instance.get_response_body_api()),
                             )
        def post(self, request: Request):
            d = ChatMessageSerializer.Instance(data=request.data)
            return result.success(d.save())

    class Batch(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_("Save chat messages in batch"),
                             operation_id=_("Save chat messages in batch"),
                             tags=[_("User management")],
                             request_body=ChatMessageSerializer.Batch.get_request_body_api(),
                             responses=result.get_api_array_response(ChatMessageSerializer.Instance.get_response_body_api()),
                             )
        def post(self, request: Request):
            d = ChatMessageSerializer.Batch(data=request.data)
            return result.success(d.save())

    class List(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get chat messages"),
                             operation_id=_("Get chat messages"),
                             tags=[_("User management")],
                             manual_parameters=ChatMessageSerializer.Query.get_request_params_api(),
                             responses=result.get_api_array_response(ChatMessageSerializer.Query.get_response_body_api()),
                             )
        def get(self, request: Request):
            d = ChatMessageSerializer.Query(data=request.query_params)
            return result.success(d.list())
