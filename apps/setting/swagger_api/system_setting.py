# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： system_setting.py
    @date：2024/3/19 16:05
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin
from django.utils.translation import gettext_lazy as _


class SystemSettingEmailApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title=_('Email related parameters'),
                              description=_('Email related parameters'),
                              required=['email_host', 'email_port', 'email_host_user', 'email_host_password',
                                        'email_use_tls', 'email_use_ssl', 'from_email'],
                              properties={
                                  'email_host': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title=_('SMTP host'),
                                                               description=_('SMTP host')),
                                  'email_port': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                               title=_('SMTP port'),
                                                               description=_('SMTP port')),
                                  'email_host_user': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    title=_('Sender\'s email'),
                                                                    description=_('Sender\'s email')),
                                  'email_host_password': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        title=_('Password'),
                                                                        description=_('Password')),
                                  'email_use_tls': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title=_('Whether to enable TLS'),
                                                                  description=_('Whether to enable TLS')),
                                  'email_use_ssl': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title=_('Whether to enable SSL'),
                                                                  description=_('Whether to enable SSL')),
                                  'from_email': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title=_('Sender\'s email'),
                                                               description=_('Sender\'s email'))
                              }
                              )

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title=_('Email related parameters'),
                              description=_('Email related parameters'),
                              required=['email_host', 'email_port', 'email_host_user', 'email_host_password',
                                        'email_use_tls', 'email_use_ssl', 'from_email'],
                              properties={
                                  'email_host': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title=_('SMTP host'),
                                                               description=_('SMTP host')),
                                  'email_port': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                               title=_('SMTP port'),
                                                               description=_('SMTP port')),
                                  'email_host_user': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    title=_('Sender\'s email'),
                                                                    description=_('Sender\'s email')),
                                  'email_host_password': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        title=_('Password'),
                                                                        description=_('Password')),
                                  'email_use_tls': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title=_('Whether to enable TLS'),
                                                                  description=_('Whether to enable TLS')),
                                  'email_use_ssl': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title=_('Whether to enable SSL'),
                                                                  description=_('Whether to enable SSL')),
                                  'from_email': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title=_('Sender\'s email'),
                                                               description=_('Sender\'s email'))
                              }
                              )


class SystemSettingLoginAuthApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title=_('LoginAuth related parameters'),
                              description=_('LoginAuth related parameters'),
                              required=['authorized_url', 'token_url', 'user_info_url', 'connect_range',
                                        'client_id', 'client_secret', 'callback_url', 'field_map', 'enable_oauth2'],
                              properties={
                                  'authorized_url': openapi.Schema(type=openapi.TYPE_STRING,
                                                                   title=_('Authorized Url'),
                                                                   description=_('Authorized Url')),
                                  'token_url': openapi.Schema(type=openapi.TYPE_STRING,
                                                              title=_('Token Url'),
                                                              description=_('Token Url')),
                                  'user_info_url': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  title=_('User Info Url'),
                                                                  description=_('User Info Url')),
                                  'connect_range': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  title=_('Connect Range'),
                                                                  description=_('Connect Range')),
                                  'client_id': openapi.Schema(type=openapi.TYPE_STRING,
                                                              title=_('Client Id'),
                                                              description=_('Client Id')),
                                  'client_secret': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  title=_('Client Secret'),
                                                                  description=_('Client Secret')),
                                  'callback_url': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 title=_('Callback Url'),
                                                                 description=_('Callback Url')),
                                  'field_map': openapi.Schema(type=openapi.TYPE_STRING,
                                                              title=_('Field Map'),
                                                              description=_('Field Map')),
                                  'enable_oauth2': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title=_('Enable Oauth2'),
                                                                  description=_('Enable Oauth2'))
                              }
                              )
