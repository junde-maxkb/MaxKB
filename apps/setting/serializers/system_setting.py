# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： system_setting.py
    @date：2024/3/19 16:29
    @desc:
"""
import secrets

from django.core.mail.backends.smtp import EmailBackend
from django.db.models import QuerySet
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from common.util.field_message import ErrMessage
from setting.models.system_management import SystemSetting, SettingType
from django.utils.translation import gettext_lazy as _


class SystemSettingSerializer(serializers.Serializer):
    class EmailSerializer(serializers.Serializer):
        @staticmethod
        def one():
            system_setting = QuerySet(SystemSetting).filter(type=SettingType.EMAIL.value).first()
            if system_setting is None:
                return {}
            return system_setting.meta

        class Create(serializers.Serializer):
            email_host = serializers.CharField(required=True, error_messages=ErrMessage.char(_('SMTP host')))
            email_port = serializers.IntegerField(required=True, error_messages=ErrMessage.char(_('SMTP port')))
            email_host_user = serializers.CharField(required=True, error_messages=ErrMessage.char(_('Sender\'s email')))
            email_host_password = serializers.CharField(required=True, error_messages=ErrMessage.char(_('Password')))
            email_use_tls = serializers.BooleanField(required=True, error_messages=ErrMessage.char(_('Whether to enable TLS')))
            email_use_ssl = serializers.BooleanField(required=True, error_messages=ErrMessage.char(_('Whether to enable SSL')))
            from_email = serializers.EmailField(required=True, error_messages=ErrMessage.char(_('Sender\'s email')))

            def is_valid(self, *, raise_exception=False):
                super().is_valid(raise_exception=True)
                try:
                    EmailBackend(self.data.get("email_host"),
                                 self.data.get("email_port"),
                                 self.data.get("email_host_user"),
                                 self.data.get("email_host_password"),
                                 self.data.get("email_use_tls"),
                                 False,
                                 self.data.get("email_use_ssl")
                                 ).open()
                except Exception as e:
                    raise AppApiException(1004, _('Email verification failed'))

            def update_or_save(self):
                self.is_valid(raise_exception=True)
                system_setting = QuerySet(SystemSetting).filter(type=SettingType.EMAIL.value).first()
                if system_setting is None:
                    system_setting = SystemSetting(type=SettingType.EMAIL.value)
                system_setting.meta = self.to_email_meta()
                system_setting.save()
                return system_setting.meta

            def to_email_meta(self):
                return {'email_host': self.data.get('email_host'),
                        'email_port': self.data.get('email_port'),
                        'email_host_user': self.data.get('email_host_user'),
                        'email_host_password': self.data.get('email_host_password'),
                        'email_use_tls': self.data.get('email_use_tls'),
                        'email_use_ssl': self.data.get('email_use_ssl'),
                        'from_email': self.data.get('from_email')
                        }

    class LoginAuthSerializer(serializers.Serializer):
        @staticmethod
        def one():
            system_setting = QuerySet(SystemSetting).filter(type=SettingType.LOGINAUTH.value).first()
            if system_setting is None:
                return {}
            return system_setting.meta

        class Create(serializers.Serializer):
            authorized_url = serializers.CharField(required=True, error_messages=ErrMessage.char(_('SMTP host')))
            token_url = serializers.CharField(required=True, error_messages=ErrMessage.char(_('SMTP port')))
            user_info_url = serializers.CharField(required=True, error_messages=ErrMessage.char(_('Sender\'s email')))
            connect_range = serializers.CharField(required=True, error_messages=ErrMessage.char(_('Password')))
            client_id = serializers.CharField(required=True, error_messages=ErrMessage.char(_('Whether to enable TLS')))
            client_secret = serializers.CharField(required=True,
                                                  error_messages=ErrMessage.char(_('Whether to enable SSL')))
            callback_url = serializers.CharField(required=True, error_messages=ErrMessage.char(_('Sender\'s email')))
            field_map = serializers.CharField(required=True, error_messages=ErrMessage.char(_('Sender\'s email')))
            enable_oauth2 = serializers.BooleanField(required=True,
                                                     error_messages=ErrMessage.char(_('Sender\'s email')))

            def is_valid(self, *, raise_exception=False):
                super().is_valid(raise_exception=True)

            def update_or_save(self, request):
                self.is_valid(raise_exception=True)
                system_setting = QuerySet(SystemSetting).filter(type=SettingType.LOGINAUTH.value).first()
                if system_setting is None:
                    system_setting = SystemSetting(type=SettingType.LOGINAUTH.value)
                system_setting.meta = self.to_login_auth_meta()
                system_setting.save()
                if system_setting.meta.get("enable_oauth2"):
                    state = secrets.token_urlsafe(16)
                    request.session['oauth_state'] = state  # 存储到session
                    params = {
                        'client_id': system_setting.meta.get("client_id"),
                        'redirect_uri': system_setting.meta.get("callback_url"),
                        'scope': system_setting.meta.get("connect_range"),  # 按需申请权限
                        'state': state,
                        'response_type': 'code'
                    }
                    auth_url = f"{system_setting.meta.get('authorized_url')}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
                    system_setting.meta.update({"auth_url": auth_url})
                return system_setting.meta

            def to_login_auth_meta(self):
                return {'authorized_url': self.data.get('authorized_url'),
                        'token_url': self.data.get('token_url'),
                        'user_info_url': self.data.get('user_info_url'),
                        'connect_range': self.data.get('connect_range'),
                        'client_id': self.data.get('client_id'),
                        'client_secret': self.data.get('client_secret'),
                        'callback_url': self.data.get('callback_url'),
                        'field_map': self.data.get('field_map'),
                        'enable_oauth2': self.data.get('enable_oauth2')
                        }
