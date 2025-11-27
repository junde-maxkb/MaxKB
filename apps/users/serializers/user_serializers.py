# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： team_serializers.py
    @date：2023/9/5 16:32
    @desc:
"""
import datetime
import os
import random
import re
import uuid

from django.conf import settings
from django.core import validators, signing, cache
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend
from django.db import transaction
from django.db.models import Q, QuerySet, Prefetch
from drf_yasg import openapi
from rest_framework import serializers

from application.models import Application
from common.constants.authentication_type import AuthenticationType
from common.constants.exception_code_constants import ExceptionCodeConstants
from common.constants.permission_constants import RoleConstants, get_permission_list_by_role
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.models.db_model_manage import DBModelManage
from common.response.result import get_api_response
from common.util.common import valid_license
from common.util.field_message import ErrMessage
from common.util.lock import lock
from dataset.models import DataSet, Document, Paragraph, Problem, ProblemParagraphMapping
from embedding.task import delete_embedding_by_dataset_id_list
from function_lib.models.function import FunctionLib
from setting.models import Team, SystemSetting, SettingType, Model, TeamMember, TeamMemberPermission
from smartdoc.conf import PROJECT_DIR
from users.models.user import User, password_encrypt, get_user_dynamics_permission
from users.models.chat_history import ChatHistory, ChatMessage
from django.utils.translation import gettext_lazy as _, gettext, to_locale
from django.utils.translation import get_language
user_cache = cache.caches['user_cache']


class SystemSerializer(ApiMixin, serializers.Serializer):
    @staticmethod
    def get_profile():
        version = os.environ.get('MAXKB_VERSION')
        xpack_cache = DBModelManage.get_model('xpack_cache')
        return {'version': version, 'IS_XPACK': hasattr(settings, 'IS_XPACK'),
                'XPACK_LICENSE_IS_VALID': False if xpack_cache is None else xpack_cache.get('XPACK_LICENSE_IS_VALID',
                                                                                            False)}

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[],
            properties={
                'version': openapi.Schema(type=openapi.TYPE_STRING, title=_("System version number"),
                                          description=_("System version number")),
            }
        )


class LoginSerializer(ApiMixin, serializers.Serializer):
    username = serializers.CharField(required=True,
                                     error_messages=ErrMessage.char(_("Username")))

    password = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Password")))

    def is_valid(self, *, raise_exception=False):
        """
        校验参数
        :param raise_exception: Whether to throw an exception can only be True
        :return: User information
        """
        super().is_valid(raise_exception=True)
        username = self.data.get("username")
        password = password_encrypt(self.data.get("password"))
        user = QuerySet(User).filter(Q(username=username,
                                       password=password) | Q(email=username,
                                                              password=password)).first()
        if user is None:
            raise ExceptionCodeConstants.INCORRECT_USERNAME_AND_PASSWORD.value.to_app_api_exception()
        if not user.is_active:
            raise AppApiException(1005, _("The user has been disabled, please contact the administrator!"))
        return user

    def get_user_token(self):
        """
        Get user token
        :return: User Token (authentication information)
        """
        user = self.is_valid()
        token = signing.dumps({'username': user.username, 'id': str(user.id), 'email': user.email,
                               'type': AuthenticationType.USER.value})
        return token

    class Meta:
        model = User
        fields = '__all__'

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, title=_("Username"), description=_("Username")),
                'password': openapi.Schema(type=openapi.TYPE_STRING, title=_("Password"), description=_("Password"))
            }
        )

    def get_response_body_api(self):
        return get_api_response(openapi.Schema(
            type=openapi.TYPE_STRING,
            title="token",
            default="xxxx",
            description="认证token"
        ))


class RegisterSerializer(ApiMixin, serializers.Serializer):
    """
    Register request object
    """
    email = serializers.EmailField(
        required=True,
        error_messages=ErrMessage.char(_("Email")),
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

    username = serializers.CharField(required=True,
                                     error_messages=ErrMessage.char(_("Username")),
                                     max_length=20,
                                     min_length=6,
                                     validators=[
                                         validators.RegexValidator(regex=re.compile("^.{6,20}$"),
                                                                   message=_("Username must be 6-20 characters long"))
                                     ])
    password = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Password")),
                                     validators=[validators.RegexValidator(regex=re.compile(
                                         "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                         "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                         , message=_(
                                             "The password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."))])

    re_password = serializers.CharField(required=True,
                                        error_messages=ErrMessage.char(_("Confirm Password")),
                                        validators=[validators.RegexValidator(regex=re.compile(
                                            "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                            "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                            , message=_(
                                                "The password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."))])

    code = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Verification code")))

    class Meta:
        model = User
        fields = '__all__'

    @lock(lock_key=lambda this, raise_exception: (
            this.initial_data.get("email") + ":register"

    ))
    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        if self.data.get('password') != self.data.get('re_password'):
            raise ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.to_app_api_exception()
        username = self.data.get("username")
        email = self.data.get("email")
        code = self.data.get("code")
        code_cache_key = email + ":register"
        cache_code = user_cache.get(code_cache_key)
        if code != cache_code:
            raise ExceptionCodeConstants.CODE_ERROR.value.to_app_api_exception()
        u = QuerySet(User).filter(Q(username=username) | Q(email=email)).first()
        if u is not None:
            if u.email == email:
                raise ExceptionCodeConstants.EMAIL_IS_EXIST.value.to_app_api_exception()
            if u.username == username:
                raise ExceptionCodeConstants.USERNAME_IS_EXIST.value.to_app_api_exception()

        return True

    @valid_license(model=User, count=20000000,
                   message=_(
                       "The community version supports up to 2 users. If you need more users, please contact us (https://fit2cloud.com/)."))
    @transaction.atomic
    def save(self, **kwargs):
        m = User(
            **{'id': uuid.uuid1(), 'email': self.data.get("email"), 'username': self.data.get("username"),
               'role': RoleConstants.USER.name})
        m.set_password(self.data.get("password"))
        m.save()
        Team(**{'user': m, 'name': m.username + _("team")}).save()
        email = self.data.get("email")
        code_cache_key = email + ":register"
        user_cache.delete(code_cache_key)

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password', 're_password', 'code'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, title=_("Username"), description=_("Username")),
                'email': openapi.Schema(type=openapi.TYPE_STRING, title=_("Email"), description=_("Email")),
                'password': openapi.Schema(type=openapi.TYPE_STRING, title=_("Password"), description=_("Password")),
                're_password': openapi.Schema(type=openapi.TYPE_STRING, title=_("Confirm Password"),
                                              description=_("Confirm Password")),
                'code': openapi.Schema(type=openapi.TYPE_STRING, title=_("Verification code"),
                                       description=_("Verification code"))
            }
        )


class CheckCodeSerializer(ApiMixin, serializers.Serializer):
    """
     校验验证码
    """
    email = serializers.EmailField(
        required=True,
        error_messages=ErrMessage.char(_("Email")),
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])
    code = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Verification code")))

    type = serializers.CharField(required=True,
                                 error_messages=ErrMessage.char(_("Type")),
                                 validators=[
                                     validators.RegexValidator(regex=re.compile("^register|reset_password$"),
                                                               message=_(
                                                                   "The type only supports register|reset_password"),
                                                               code=500)
                                 ])

    def is_valid(self, *, raise_exception=False):
        super().is_valid()
        value = user_cache.get(self.data.get("email") + ":" + self.data.get("type"))
        if value is None or value != self.data.get("code"):
            raise ExceptionCodeConstants.CODE_ERROR.value.to_app_api_exception()
        return True

    class Meta:
        model = User
        fields = '__all__'

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'code', 'type'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, title=_("Email"), description=_("Email")),
                'code': openapi.Schema(type=openapi.TYPE_STRING, title=_("Verification code"),
                                       description=_("Verification code")),
                'type': openapi.Schema(type=openapi.TYPE_STRING, title=_("Type"), description="register|reset_password")
            }
        )

    def get_response_body_api(self):
        return get_api_response(openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            title=_('Is it successful'),
            default=True,
            description=_('Error message')))


class SwitchLanguageSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_('user id')), )
    language = serializers.CharField(required=True, error_messages=ErrMessage.char(_('language')))

    def switch(self):
        self.is_valid(raise_exception=True)
        language = self.data.get('language')
        support_language_list = ['zh-CN', 'zh-Hant', 'en-US']
        if not support_language_list.__contains__(language):
            raise AppApiException(500, _('language only support:') + ','.join(support_language_list))
        QuerySet(User).filter(id=self.data.get('user_id')).update(language=language)


class RePasswordSerializer(ApiMixin, serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages=ErrMessage.char(_("Email")),
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

    code = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Verification code")))

    password = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Password")),
                                     validators=[validators.RegexValidator(regex=re.compile(
                                         "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                         "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                         , message=_(
                                             "The confirmation password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."))])

    re_password = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Confirm Password")),
                                        validators=[validators.RegexValidator(regex=re.compile(
                                            "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                            "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                            , message=_(
                                                "The confirmation password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."))]
                                        )

    class Meta:
        model = User
        fields = '__all__'

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        email = self.data.get("email")
        cache_code = user_cache.get(email + ':reset_password')
        if self.data.get('password') != self.data.get('re_password'):
            raise AppApiException(ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.code,
                                  ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.message)
        if cache_code != self.data.get('code'):
            raise AppApiException(ExceptionCodeConstants.CODE_ERROR.value.code,
                                  ExceptionCodeConstants.CODE_ERROR.value.message)
        return True

    def reset_password(self):
        """
        修改密码
        :return: 是否成功
        """
        if self.is_valid():
            email = self.data.get("email")
            QuerySet(User).filter(email=email).update(
                password=password_encrypt(self.data.get('password')))
            code_cache_key = email + ":reset_password"
            # 删除验证码缓存
            user_cache.delete(code_cache_key)
            return True

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'code', "password", 're_password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, title=_("Email"), description=_("Email")),
                'code': openapi.Schema(type=openapi.TYPE_STRING, title=_("Verification code"),
                                       description=_("Verification code")),
                'password': openapi.Schema(type=openapi.TYPE_STRING, title=_("Password"), description=_("Password")),
                're_password': openapi.Schema(type=openapi.TYPE_STRING, title=_("Confirm Password"),
                                              description=_("Confirm Password"))
            }
        )


class SendEmailSerializer(ApiMixin, serializers.Serializer):
    email = serializers.EmailField(
        required=True
        , error_messages=ErrMessage.char(_("Email")),
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

    type = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Type")), validators=[
        validators.RegexValidator(regex=re.compile("^register|reset_password$"),
                                  message=_("The type only supports register|reset_password"), code=500)
    ])

    class Meta:
        model = User
        fields = '__all__'

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=raise_exception)
        user_exists = QuerySet(User).filter(email=self.data.get('email')).exists()
        if not user_exists and self.data.get('type') == 'reset_password':
            raise ExceptionCodeConstants.EMAIL_IS_NOT_EXIST.value.to_app_api_exception()
        elif user_exists and self.data.get('type') == 'register':
            raise ExceptionCodeConstants.EMAIL_IS_EXIST.value.to_app_api_exception()
        code_cache_key = self.data.get('email') + ":" + self.data.get("type")
        code_cache_key_lock = code_cache_key + "_lock"
        ttl = user_cache.ttl(code_cache_key_lock)
        if ttl is not None:
            raise AppApiException(500, _("Do not send emails again within {seconds} seconds").format(
                seconds=int(ttl.total_seconds())))
        return True

    def send(self):
        """
        发送邮件
        :return:   是否发送成功
        :exception 发送失败异常
        """
        email = self.data.get("email")
        state = self.data.get("type")
        # 生成随机验证码
        code = "".join(list(map(lambda i: random.choice(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
                                                         ]), range(6))))
        # 获取邮件模板
        language = get_language()
        file = open(
            os.path.join(PROJECT_DIR, "apps", "common", 'template', f'email_template_{to_locale(language)}.html'), "r",
            encoding='utf-8')
        content = file.read()
        file.close()
        code_cache_key = email + ":" + state
        code_cache_key_lock = code_cache_key + "_lock"
        # 设置缓存
        user_cache.set(code_cache_key_lock, code, timeout=datetime.timedelta(minutes=1))
        system_setting = QuerySet(SystemSetting).filter(type=SettingType.EMAIL.value).first()
        if system_setting is None:
            user_cache.delete(code_cache_key_lock)
            raise AppApiException(1004,
                                  _("The email service has not been set up. Please contact the administrator to set up the email service in [Email Settings]."))
        try:
            connection = EmailBackend(system_setting.meta.get("email_host"),
                                      system_setting.meta.get('email_port'),
                                      system_setting.meta.get('email_host_user'),
                                      system_setting.meta.get('email_host_password'),
                                      system_setting.meta.get('email_use_tls'),
                                      False,
                                      system_setting.meta.get('email_use_ssl')
                                      )
            # 发送邮件
            send_mail(_('【Intelligent knowledge base question and answer system-{action}】').format(
                action=_('User registration') if state == 'register' else _('Change password')),
                '',
                html_message=f'{content.replace("${code}", code)}',
                from_email=system_setting.meta.get('from_email'),
                recipient_list=[email], fail_silently=False, connection=connection)
        except Exception as e:
            user_cache.delete(code_cache_key_lock)
            raise AppApiException(500, f"{str(e)}" + _("Email sending failed"))
        user_cache.set(code_cache_key, code, timeout=datetime.timedelta(minutes=30))
        return True

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'type'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, title=_("Email"), description=_('Email')),
                'type': openapi.Schema(type=openapi.TYPE_STRING, title=_('Type'), description="register|reset_password")
            }
        )

    def get_response_body_api(self):
        return get_api_response(openapi.Schema(type=openapi.TYPE_STRING, default=True))


class UserProfile(ApiMixin):

    @staticmethod
    def get_user_profile(user: User):
        """
        获取用户详情
        :param user: 用户对象
        :return:
        """
        permission_list = get_user_dynamics_permission(str(user.id))
        permission_list += [p.value for p in get_permission_list_by_role(RoleConstants[user.role])]
        return {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role,
                'permissions': [str(p) for p in permission_list],
                'is_edit_password': user.password == 'd880e722c47a34d8e9fce789fc62389d' if user.role == 'ADMIN' else False,
                'language': user.language}

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'username', 'email', 'role', 'is_active'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="ID", description="ID"),
                'username': openapi.Schema(type=openapi.TYPE_STRING, title=_("Username"), description=_("Username")),
                'email': openapi.Schema(type=openapi.TYPE_STRING, title=_("Email"), description=_("Email")),
                'role': openapi.Schema(type=openapi.TYPE_STRING, title=_("Role"), description=_("Role")),
                'is_active': openapi.Schema(type=openapi.TYPE_STRING, title=_("Is active"), description=_("Is active")),
                "permissions": openapi.Schema(type=openapi.TYPE_ARRAY, title=_("Permissions"),
                                              description=_("Permissions"),
                                              items=openapi.Schema(type=openapi.TYPE_STRING))
            }
        )


class UserSerializer(ApiMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "id",
                  "username", ]

    def get_response_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'username', 'email', 'role', 'is_active'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="ID", description="ID"),
                'username': openapi.Schema(type=openapi.TYPE_STRING, title=_("Username"), description=_("Username")),
                'email': openapi.Schema(type=openapi.TYPE_STRING, title=_("Email"), description=_("Email")),
                'role': openapi.Schema(type=openapi.TYPE_STRING, title=_("Role"), description=_("Role")),
                'is_active': openapi.Schema(type=openapi.TYPE_STRING, title=_("Is active"), description=_("Is active"))
            }
        )

    class Query(ApiMixin, serializers.Serializer):
        email_or_username = serializers.CharField(required=True)

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='email_or_username',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_("Email or username"))]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['username', 'email', 'id'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title='ID', description="ID"),
                    'username': openapi.Schema(type=openapi.TYPE_STRING, title=_("Username"),
                                               description=_("Username")),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, title=_("Email"), description=_("Email"))
                }
            )

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            email_or_username = self.data.get('email_or_username')
            return [{'id': user_model.id, 'username': user_model.username, 'email': user_model.email} for user_model
                    in
                    QuerySet(User).filter(Q(username=email_or_username) | Q(email=email_or_username))]

    def listByType(self, type, user_id):
        teamIds = TeamMember.objects.filter(user_id=user_id).values_list('id', flat=True)
        targets = TeamMemberPermission.objects.filter(
            member_id__in=teamIds,
            auth_target_type=type,
            operate__contains=['USE']
        ).values_list('target', flat=True)
        prefetch_users = Prefetch('user', queryset=User.objects.only('id', 'username'))

        user_list = []
        if type == 'DATASET':
            user_list = DataSet.objects.filter(
                Q(id__in=targets) | Q(user_id=user_id)
            ).prefetch_related(prefetch_users).distinct('user_id')
        elif type == 'APPLICATION':
            user_list = Application.objects.filter(
                Q(id__in=targets) | Q(user_id=user_id)
            ).prefetch_related(prefetch_users).distinct('user_id')
        elif type == 'FUNCTION':
            user_list = FunctionLib.objects.filter(
                Q(permission_type='PUBLIC') | Q(user_id=user_id)
            ).prefetch_related(prefetch_users).distinct('user_id')

        other_users = [
            {'id': app.user.id, 'username': app.user.username}
            for app in user_list if app.user.id != user_id
        ]
        users = [
            {'id': 'all', 'username': _('All')},
            {'id': user_id, 'username': _('Me')}
        ]
        users.extend(other_users)
        return users

    @staticmethod
    def get_user_by_username(username):
        user = User.objects.filter(username=username).first()
        return user


class UserInstanceSerializer(ApiMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'is_active', 'role', 'nick_name', 'create_time', 'update_time',
                  'source']

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'username', 'email', 'phone', 'is_active', 'role', 'nick_name', 'create_time',
                      'update_time'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="ID", description="ID"),
                'username': openapi.Schema(type=openapi.TYPE_STRING, title=_("Username"), description=_("Username")),
                'email': openapi.Schema(type=openapi.TYPE_STRING, title=_("Email"), description=_("Email")),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, title=_("Phone"), description=_("Phone")),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Is active"),
                                            description=_("Is active")),
                'role': openapi.Schema(type=openapi.TYPE_STRING, title=_("Role"), description=_("Role")),
                'source': openapi.Schema(type=openapi.TYPE_STRING, title=_("Source"), description=_("Source")),
                'nick_name': openapi.Schema(type=openapi.TYPE_STRING, title=_("Name"), description=_("Name")),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Create time"),
                                              description=_("Create time")),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Update time"),
                                              description=_("Update time"))
            }
        )

    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='user_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='ID')

                ]


class UserManageSerializer(serializers.Serializer):
    class Query(ApiMixin, serializers.Serializer):
        email_or_username = serializers.CharField(required=False, allow_null=True,
                                                  error_messages=ErrMessage.char(_('Email or username')))

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='email_or_username',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description=_("Email or username"))]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['username', 'email', 'id'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title='ID', description="ID"),
                    'username': openapi.Schema(type=openapi.TYPE_STRING, title=_("Username"),
                                               description=_("Username")),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, title=_("Email"), description=_("Email"))
                }
            )

        def get_query_set(self):
            email_or_username = self.data.get('email_or_username')
            query_set = QuerySet(User)
            if email_or_username is not None:
                query_set = query_set.filter(
                    Q(username__contains=email_or_username) | Q(email__contains=email_or_username))
            query_set = query_set.order_by("-create_time")
            return query_set

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return [{'id': user_model.id, 'username': user_model.username, 'email': user_model.email} for user_model in
                    self.get_query_set()]

        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return page_search(current_page, page_size,
                               self.get_query_set(),
                               post_records_handler=lambda u: UserInstanceSerializer(u).data)

    class UserInstance(ApiMixin, serializers.Serializer):
        email = serializers.EmailField(
            required=True,
            error_messages=ErrMessage.char(_("Email")),
            validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                                  code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

        username = serializers.CharField(required=True,
                                         error_messages=ErrMessage.char(_("Username")),
                                         max_length=20,
                                         min_length=1,
                                         validators=[
                                             validators.RegexValidator(regex=re.compile("^.{1,20}$"),
                                                                       message=_(
                                                                           'Username must be 6-20 characters long'))
                                         ])
        password = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Password")),
                                         validators=[validators.RegexValidator(regex=re.compile(
                                             "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                             "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{1,20}$")
                                             , message=_(
                                                 "The password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."))])

        nick_name = serializers.CharField(required=False, error_messages=ErrMessage.char(_("Name")), max_length=64,
                                          allow_null=True, allow_blank=True)
        phone = serializers.CharField(required=False, error_messages=ErrMessage.char(_("Phone")), max_length=20,
                                      allow_null=True, allow_blank=True)

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            username = self.data.get('username')
            email = self.data.get('email')
            u = QuerySet(User).filter(Q(username=username) | Q(email=email)).first()
            if u is not None:
                if u.email == email:
                    raise ExceptionCodeConstants.EMAIL_IS_EXIST.value.to_app_api_exception()
                if u.username == username:
                    raise ExceptionCodeConstants.USERNAME_IS_EXIST.value.to_app_api_exception()

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['username', 'email', 'password'],
                properties={
                    'username': openapi.Schema(type=openapi.TYPE_STRING, title=_("Username"),
                                               description=_("Username")),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, title=_("Email"), description=_("Email")),
                    'password': openapi.Schema(type=openapi.TYPE_STRING, title=_("Password"),
                                               description=_("Password")),
                    'phone': openapi.Schema(type=openapi.TYPE_STRING, title=_("Phone"), description=_("Phone")),
                    'nick_name': openapi.Schema(type=openapi.TYPE_STRING, title=_("Name"), description=_("Name"))
                }
            )

    class UserEditInstance(ApiMixin, serializers.Serializer):
        email = serializers.EmailField(
            required=False,
            error_messages=ErrMessage.char(_("Email")),
            validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                                  code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

        nick_name = serializers.CharField(required=False, error_messages=ErrMessage.char(_("Name")), max_length=64,
                                          allow_null=True, allow_blank=True)
        phone = serializers.CharField(required=False, error_messages=ErrMessage.char(_("Phone")), max_length=20,
                                      allow_null=True, allow_blank=True)
        is_active = serializers.BooleanField(required=False, error_messages=ErrMessage.char(_("Is active")))

        def is_valid(self, *, user_id=None, raise_exception=False):
            super().is_valid(raise_exception=True)
            if self.data.get('email') is not None and QuerySet(User).filter(email=self.data.get('email')).exclude(
                    id=user_id).exists():
                raise AppApiException(1004, _('Email is already in use'))

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'email': openapi.Schema(type=openapi.TYPE_STRING, title=_("Email"), description=_("Email")),
                    'nick_name': openapi.Schema(type=openapi.TYPE_STRING, title=_("Name"), description=_("Name")),
                    'phone': openapi.Schema(type=openapi.TYPE_STRING, title=_("Phone"), description=_("Phone")),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Is active"),
                                                description=_("Is active")),
                }
            )

    class RePasswordInstance(ApiMixin, serializers.Serializer):
        password = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Password")),
                                         validators=[validators.RegexValidator(regex=re.compile(
                                             "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                             "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                             , message=_(
                                                 "The password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."))])
        re_password = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Confirm Password")),
                                            validators=[validators.RegexValidator(regex=re.compile(
                                                "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                                "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                                , message=_(
                                                    "The confirmation password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."))]
                                            )

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['password', 're_password'],
                properties={
                    'password': openapi.Schema(type=openapi.TYPE_STRING, title=_("Password"),
                                               description=_("Password")),
                    're_password': openapi.Schema(type=openapi.TYPE_STRING, title=_("Confirm Password"),
                                                  description=_("Confirm Password")),
                }
            )

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if self.data.get('password') != self.data.get('re_password'):
                raise ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.to_app_api_exception()

    class SetAdminInstance(ApiMixin, serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_('user id')))

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=["user_id"],
            )

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if self.data.get('id') != self.data.get('re_password'):
                raise ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.to_app_api_exception()

    @valid_license(model=User, count=20000000,
                   message=_(
                       'The community version supports up to 2 users. If you need more users, please contact us (https://fit2cloud.com/).'))
    @transaction.atomic
    def save(self, instance, with_valid=True):
        if with_valid:
            UserManageSerializer.UserInstance(data=instance).is_valid(raise_exception=True)

        user = User(id=uuid.uuid1(), email=instance.get('email'),
                    phone="" if instance.get('phone') is None else instance.get('phone'),
                    nick_name="" if instance.get('nick_name') is None else instance.get('nick_name')
                    , username=instance.get('username'), password=password_encrypt(instance.get('password')),
                    role=RoleConstants.USER.name, source="LOCAL",
                    is_active=True)
        user.save()
        # 初始化用户团队
        # Team(**{'user': user, 'name': user.username + _('team')}).save()
        return UserInstanceSerializer(user).data

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True, error_messages=ErrMessage.char("ID"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(User).filter(id=self.data.get('id')).exists():
                raise AppApiException(1004, _('User does not exist'))

        @transaction.atomic
        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                user = QuerySet(User).filter(id=self.data.get('id')).first()
                if user.role == RoleConstants.ADMIN.name:
                    raise AppApiException(1004, _('Unable to delete administrator'))
            user_id = self.data.get('id')

            team_member_list = QuerySet(TeamMember).filter(Q(user_id=user_id) | Q(team_id=user_id))
            # 删除团队成员权限
            QuerySet(TeamMemberPermission).filter(
                member_id__in=[team_member.id for team_member in team_member_list]).delete()
            # 删除团队成员
            team_member_list.delete()
            # 删除应用相关 因为应用相关都是级联删除所以不需要手动删除
            QuerySet(Application).filter(user_id=self.data.get('id')).delete()
            # 删除数据集相关
            dataset_list = QuerySet(DataSet).filter(user_id=self.data.get('id'))
            dataset_id_list = [str(dataset.id) for dataset in dataset_list]
            QuerySet(Document).filter(dataset_id__in=dataset_id_list).delete()
            QuerySet(Paragraph).filter(dataset_id__in=dataset_id_list).delete()
            QuerySet(ProblemParagraphMapping).filter(dataset_id__in=dataset_id_list).delete()
            QuerySet(Problem).filter(dataset_id__in=dataset_id_list).delete()
            delete_embedding_by_dataset_id_list(dataset_id_list)
            dataset_list.delete()
            # 删除团队
            QuerySet(Team).filter(user_id=self.data.get('id')).delete()
            # 删除模型
            QuerySet(Model).filter(user_id=self.data.get('id')).delete()
            # 删除用户
            QuerySet(User).filter(id=self.data.get('id')).delete()
            return True

        def edit(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                UserManageSerializer.UserEditInstance(data=instance).is_valid(user_id=self.data.get('id'),
                                                                              raise_exception=True)

            user = QuerySet(User).filter(id=self.data.get('id')).first()
            if user.role == RoleConstants.ADMIN.name and 'is_active' in instance and instance.get(
                    'is_active') is not None:
                raise AppApiException(1004, _('Cannot modify administrator status'))
            update_keys = ['email', 'nick_name', 'phone', 'is_active']
            for update_key in update_keys:
                if update_key in instance and instance.get(update_key) is not None:
                    user.__setattr__(update_key, instance.get(update_key))
            user.save()
            return UserInstanceSerializer(user).data

        def one(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            user = QuerySet(User).filter(id=self.data.get('id')).first()
            return UserInstanceSerializer(user).data

        def re_password(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                UserManageSerializer.RePasswordInstance(data=instance).is_valid(raise_exception=True)
            user = QuerySet(User).filter(id=self.data.get('id')).first()
            user.password = password_encrypt(instance.get('password'))
            user.save()
            return True

        def set_admin(self, instance, operate_user_id, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True),
                user = QuerySet(User).filter(id=operate_user_id).first()
                print("user", user)
                if user.role != RoleConstants.ADMIN.name:
                    raise AppApiException(1004, _('User is not admin'))
            user = QuerySet(User).filter(id=self.data.get('id')).first()
            user.role = "ADMIN"
            user.save()
            return True


class ChatHistorySerializer(ApiMixin, serializers.Serializer):
    """
    历史聊天记录序列化器
    """
    
    class Query(ApiMixin, serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("User ID")))
        keyword = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                        error_messages=ErrMessage.char(_("Search Keyword")))
        
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='user_id',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_("User ID")),
                    openapi.Parameter(name='keyword',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description=_("Search Keyword"))]
        
        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'user_id', 'application_name', 'title', 'create_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title='ID', description="ID"),
                    'user_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("User ID"), description=_("User ID")),
                    'application_name': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application Name"), 
                                                      description=_("Application Name")),
                    'title': openapi.Schema(type=openapi.TYPE_STRING, title=_("Title"), description=_("Title")),
                    'message_count': openapi.Schema(type=openapi.TYPE_INTEGER, title=_("Message Count"), 
                                                    description=_("Message Count")),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Create Time"), 
                                                  description=_("Create Time")),
                }
            )
        
        def get_query_set(self):
            user_id = self.data.get('user_id')
            keyword = self.data.get('keyword')
            
            query_set = QuerySet(ChatHistory).filter(user_id=user_id)
            
            # 如果有搜索关键词，搜索标题和应用名称
            if keyword and keyword.strip():
                query_set = query_set.filter(
                    Q(title__icontains=keyword) | Q(application_name__icontains=keyword)
                )
            
            query_set = query_set.order_by("-create_time")
            return query_set
        
        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            result = []
            for history in self.get_query_set():
                # 动态计算实际的消息数量，确保数据准确
                actual_count = QuerySet(ChatMessage).filter(chat_history_id=history.id).count()
                # 如果计算出的数量与存储的数量不一致，更新数据库
                if actual_count != history.message_count:
                    history.message_count = actual_count
                    history.save()
                
                result.append({
                    'id': str(history.id),
                    'user_id': str(history.user_id),
                    'application_name': history.application_name,
                    'title': history.title or history.application_name,
                    'message_count': actual_count,
                    'create_time': history.create_time.strftime('%Y-%m-%d %H:%M:%S') if history.create_time else None
                })
            return result
        
        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            
            def post_records_handler(h):
                # 动态计算实际的消息数量，确保数据准确
                actual_count = QuerySet(ChatMessage).filter(chat_history_id=h.id).count()
                # 如果计算出的数量与存储的数量不一致，更新数据库
                if actual_count != h.message_count:
                    h.message_count = actual_count
                    h.save()
                
                return {
                    'id': str(h.id),
                    'user_id': str(h.user_id),
                    'application_name': h.application_name,
                    'title': h.title or h.application_name,
                    'message_count': actual_count,
                    'create_time': h.create_time.strftime('%Y-%m-%d %H:%M:%S') if h.create_time else None
                }
            
            return page_search(current_page, page_size,
                               self.get_query_set(),
                               post_records_handler=post_records_handler)
    
    class Instance(ApiMixin, serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("User ID")))
        application_name = serializers.CharField(required=True, max_length=128, 
                                                  error_messages=ErrMessage.char(_("Application Name")))
        title = serializers.CharField(required=False, max_length=256, allow_blank=True, 
                                      error_messages=ErrMessage.char(_("Title")))
        message_count = serializers.IntegerField(required=False, default=0)
        
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['user_id', 'application_name'],
                properties={
                    'user_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("User ID"), 
                                              description=_("User ID")),
                    'application_name': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application Name"), 
                                                        description=_("Application Name")),
                    'title': openapi.Schema(type=openapi.TYPE_STRING, title=_("Title"), description=_("Title")),
                    'message_count': openapi.Schema(type=openapi.TYPE_INTEGER, title=_("Message Count"), 
                                                    description=_("Message Count")),
                }
            )
        
        def save(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            user_id = self.data.get('user_id')
            user = QuerySet(User).filter(id=user_id).first()
            if user is None:
                raise AppApiException(500, _("User does not exist"))
            
            chat_history = ChatHistory(
                user=user,
                application_name=self.data.get('application_name'),
                title=self.data.get('title', ''),
                message_count=self.data.get('message_count', 0)
            )
            chat_history.save()
            return {
                'id': str(chat_history.id),
                'user_id': str(chat_history.user_id),
                'application_name': chat_history.application_name,
                'title': chat_history.title,
                'message_count': chat_history.message_count,
                'create_time': chat_history.create_time.strftime('%Y-%m-%d %H:%M:%S') if chat_history.create_time else None
            }


class ChatMessageSerializer(ApiMixin, serializers.Serializer):
    """
    聊天消息序列化器
    """
    
    class Instance(ApiMixin, serializers.Serializer):
        chat_history_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("Chat History ID")))
        role = serializers.CharField(required=True, max_length=20, error_messages=ErrMessage.char(_("Role")))
        content = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Content")))
        message_index = serializers.IntegerField(required=False, default=0)
        
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['chat_history_id', 'role', 'content'],
                properties={
                    'chat_history_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Chat History ID"), 
                                                      description=_("Chat History ID")),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, title=_("Role"), 
                                          description=_("Role: user, assistant, or system")),
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title=_("Content"), 
                                             description=_("Message content")),
                    'message_index': openapi.Schema(type=openapi.TYPE_INTEGER, title=_("Message Index"), 
                                                    description=_("Message index for ordering")),
                }
            )
        
        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'chat_history_id', 'role', 'content', 'message_index'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title='ID', description="ID"),
                    'chat_history_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Chat History ID"), 
                                                      description=_("Chat History ID")),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, title=_("Role"), 
                                          description=_("Role: user, assistant, or system")),
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title=_("Content"), 
                                             description=_("Message content")),
                    'message_index': openapi.Schema(type=openapi.TYPE_INTEGER, title=_("Message Index"), 
                                                    description=_("Message index for ordering")),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Create Time"), 
                                                  description=_("Create Time")),
                }
            )
        
        def save(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            chat_history_id = self.data.get('chat_history_id')
            chat_history = QuerySet(ChatHistory).filter(id=chat_history_id).first()
            if chat_history is None:
                raise AppApiException(500, _("Chat history does not exist"))
            
            # 如果没有提供message_index，自动计算下一个序号
            message_index = self.data.get('message_index')
            if message_index is None or message_index == 0:
                last_message = QuerySet(ChatMessage).filter(chat_history_id=chat_history_id).order_by('-message_index').first()
                message_index = (last_message.message_index + 1) if last_message else 1
            
            chat_message = ChatMessage(
                chat_history=chat_history,
                role=self.data.get('role'),
                content=self.data.get('content'),
                message_index=message_index
            )
            chat_message.save()
            
            # 更新聊天记录的消息数量
            actual_count = QuerySet(ChatMessage).filter(chat_history_id=chat_history_id).count()
            chat_history.message_count = actual_count
            chat_history.save()
            
            return {
                'id': str(chat_message.id),
                'chat_history_id': str(chat_message.chat_history_id),
                'role': chat_message.role,
                'content': chat_message.content,
                'message_index': chat_message.message_index,
                'create_time': chat_message.create_time.strftime('%Y-%m-%d %H:%M:%S') if chat_message.create_time else None
            }
    
    class Batch(ApiMixin, serializers.Serializer):
        chat_history_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("Chat History ID")))
        messages = serializers.ListField(
            child=serializers.DictField(),
            required=True,
            error_messages=ErrMessage.char(_("Messages"))
        )
        
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['chat_history_id', 'messages'],
                properties={
                    'chat_history_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Chat History ID"), 
                                                      description=_("Chat History ID")),
                    'messages': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'role': openapi.Schema(type=openapi.TYPE_STRING, title=_("Role")),
                                'content': openapi.Schema(type=openapi.TYPE_STRING, title=_("Content")),
                                'message_index': openapi.Schema(type=openapi.TYPE_INTEGER, title=_("Message Index")),
                            }
                        ),
                        title=_("Messages"),
                        description=_("List of messages to save")
                    ),
                }
            )
        
        def save(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            chat_history_id = self.data.get('chat_history_id')
            chat_history = QuerySet(ChatHistory).filter(id=chat_history_id).first()
            if chat_history is None:
                raise AppApiException(500, _("Chat history does not exist"))
            
            messages_data = self.data.get('messages', [])
            saved_messages = []
            
            with transaction.atomic():
                for idx, msg_data in enumerate(messages_data):
                    role = msg_data.get('role', 'user')
                    content = msg_data.get('content', '')
                    message_index = msg_data.get('message_index', idx + 1)
                    
                    chat_message = ChatMessage(
                        chat_history=chat_history,
                        role=role,
                        content=content,
                        message_index=message_index
                    )
                    chat_message.save()
                    saved_messages.append({
                        'id': str(chat_message.id),
                        'role': chat_message.role,
                        'content': chat_message.content,
                        'message_index': chat_message.message_index,
                        'create_time': chat_message.create_time.strftime('%Y-%m-%d %H:%M:%S') if chat_message.create_time else None
                    })
                
                # 更新聊天记录的消息数量
                actual_count = QuerySet(ChatMessage).filter(chat_history_id=chat_history_id).count()
                chat_history.message_count = actual_count
                chat_history.save()
            
            return saved_messages
    
    class Query(ApiMixin, serializers.Serializer):
        chat_history_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("Chat History ID")))
        
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='chat_history_id',
                                    in_=openapi.IN_QUERY,
                                    type=openapi.TYPE_STRING,
                                    required=True,
                                    description=_("Chat History ID"))]
        
        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'chat_history_id', 'role', 'content', 'message_index'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title='ID', description="ID"),
                    'chat_history_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Chat History ID"), 
                                                      description=_("Chat History ID")),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, title=_("Role"), 
                                          description=_("Role: user, assistant, or system")),
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title=_("Content"), 
                                             description=_("Message content")),
                    'message_index': openapi.Schema(type=openapi.TYPE_INTEGER, title=_("Message Index"), 
                                                    description=_("Message index for ordering")),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Create Time"), 
                                                  description=_("Create Time")),
                }
            )
        
        def get_query_set(self):
            chat_history_id = self.data.get('chat_history_id')
            query_set = QuerySet(ChatMessage).filter(chat_history_id=chat_history_id)
            query_set = query_set.order_by("message_index", "create_time")
            return query_set
        
        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return [{
                'id': str(msg.id),
                'chat_history_id': str(msg.chat_history_id),
                'role': msg.role,
                'content': msg.content,
                'message_index': msg.message_index,
                'create_time': msg.create_time.strftime('%Y-%m-%d %H:%M:%S') if msg.create_time else None
            } for msg in self.get_query_set()]
