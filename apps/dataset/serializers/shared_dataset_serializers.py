# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： shared_dataset_serializers.py
    @date：2024/3/21
    @desc: 共享知识库序列化器
"""
import io
import logging
import os.path
import re
import traceback
import uuid
import zipfile
from functools import reduce
from tempfile import TemporaryDirectory
from typing import Dict, List
from urllib.parse import urlparse

from celery_once import AlreadyQueued
from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.db import transaction, models
from django.db.models import QuerySet
from django.db.models.functions import Reverse, Substr
from django.http import HttpResponse
from drf_yasg import openapi
from rest_framework import serializers

from application.models import ApplicationDatasetMapping
from common.config.embedding_config import VectorStore
from common.db.search import get_dynamics_model, native_page_search, native_search
from common.db.sql_execute import select_list
from common.event import ListenerManagement
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.util.common import post, flat_map, valid_license, parse_image
from common.util.field_message import ErrMessage
from common.util.file_util import get_file_content
from common.util.fork import ChildLink, Fork
from common.util.split_model import get_split_model
from dataset.models.data_set import DataSet, Document, Paragraph, Problem, Type, ProblemParagraphMapping, TaskType, \
    State, File, Image, DatasetShare
from dataset.serializers.common_serializers import list_paragraph, MetaSerializer, ProblemParagraphManage, \
    get_embedding_model_by_dataset_id, get_embedding_model_id_by_dataset_id, write_image, zip_dir, \
    GenerateRelatedSerializer
from dataset.serializers.document_serializers import DocumentSerializers, DocumentInstanceSerializer
from dataset.task import sync_web_dataset, sync_replace_web_dataset, generate_related_by_dataset_id
from embedding.models import SearchMode
from embedding.task import embedding_by_dataset, delete_embedding_by_dataset
from setting.models import AuthOperate, Model
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext_lazy as _


class SharedDataSetSerializers(serializers.ModelSerializer):
    class Meta:
        model = DataSet
        fields = ['id', 'name', 'desc', 'meta', 'create_time', 'update_time']

    class Application(ApiMixin, serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_('user id')))
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_('dataset id')))

        @staticmethod
        def get_request_params_api():
            return [
                openapi.Parameter(name='dataset_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('dataset id')),
            ]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'name', 'desc', 'model_id', 'multiple_rounds_dialogue', 'user_id', 'status',
                          'create_time',
                          'update_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="", description=_('id')),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title=_('application name'),
                                           description=_('application name')),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="_('application description')",
                                           description="_('application description')"),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title=_('model id'),
                                               description=_('model id')),
                    "multiple_rounds_dialogue": openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                               title=_('Whether to start multiple rounds of dialogue'),
                                                               description=_(
                                                                   'Whether to start multiple rounds of dialogue')),
                    'prologue': openapi.Schema(type=openapi.TYPE_STRING, title=_('opening remarks'),
                                               description=_('opening remarks')),
                    'example': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                              title=_('example'), description=_('example')),
                    'user_id': openapi.Schema(type=openapi.TYPE_STRING, title=_('User id'), description=_('User id')),
                    'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_('Whether to publish'),
                                             description=_('Whether to publish')),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('create time'),
                                                  description=_('create time')),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('update time'),
                                                  description=_('update time'))
                }
            )

    class Query(ApiMixin, serializers.Serializer):
        """
        查询对象
        """
        name = serializers.CharField(required=False,
                                     error_messages=ErrMessage.char(_('dataset name')),
                                     max_length=64,
                                     min_length=1)

        desc = serializers.CharField(required=False,
                                     error_messages=ErrMessage.char(_('dataset description')),
                                     max_length=256,
                                     min_length=1,
                                     )

        user_id = serializers.CharField(required=True)
        select_user_id = serializers.CharField(required=False)
        dataset_ids = serializers.ListField(required=False, child=serializers.UUIDField(), allow_empty=True)

        def get_query_set(self):
            user_id = self.data.get("user_id")
            query_set_dict = {}
            query_set = QuerySet(model=get_dynamics_model(
                {'temp.name': models.CharField(), 'temp.desc': models.CharField(),
                 "document_temp.char_length": models.IntegerField(), 'temp.create_time': models.DateTimeField(),
                 'temp.user_id': models.CharField(), 'temp.id': models.CharField()}))
            if "desc" in self.data and self.data.get('desc') is not None:
                query_set = query_set.filter(**{'temp.desc__icontains': self.data.get("desc")})
            if "name" in self.data and self.data.get('name') is not None:
                query_set = query_set.filter(**{'temp.name__icontains': self.data.get("name")})
            if "select_user_id" in self.data and self.data.get('select_user_id') is not None:
                query_set = query_set.filter(**{'temp.user_id__exact': self.data.get("select_user_id")})
            if "dataset_ids" in self.data and self.data.get('dataset_ids'):
                query_set = query_set.filter(**{'temp.id__in': self.data.get("dataset_ids")})
            query_set = query_set.order_by("-temp.create_time", "temp.id")
            query_set_dict['default_sql'] = query_set

            query_set_dict['dataset_custom_sql'] = QuerySet(model=get_dynamics_model(
                {'dataset.user_id': models.CharField(),
                 })).filter(
                **{'dataset.user_id': user_id}
            )

            query_set_dict['team_member_permission_custom_sql'] = QuerySet(model=get_dynamics_model(
                {'user_id': models.CharField(),
                 'team_member_permission.auth_target_type': models.CharField(),
                 'team_member_permission.operate': ArrayField(verbose_name=_('permission'),
                                                              base_field=models.CharField(max_length=256,
                                                                                          blank=True,
                                                                                          choices=AuthOperate.choices,
                                                                                          default=AuthOperate.USE)
                                                              )})).filter(
                **{'user_id': user_id, 'team_member_permission.operate__contains': ['USE'],
                   'team_member_permission.auth_target_type': 'DATASET'})

            # 添加共享知识库的查询
            query_set_dict['datasetshare_custom_sql'] = QuerySet(
                model=get_dynamics_model({'shared_with_id': models.CharField(),
                                        'permission': models.CharField()})).filter(
                **{'shared_with_id': user_id, 
                'permission__in': ['WRITE', 'READ', 'MANAGE']}
            )

            return query_set_dict

        def page(self, current_page: int, page_size: int):
            return native_page_search(current_page, page_size, self.get_query_set(), select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset.sql')),
                                      post_records_handler=lambda r: r)

        def list(self):
            return native_search(self.get_query_set(), select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset.sql')))

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description=_('dataset name')),
                    openapi.Parameter(name='desc',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description=_('dataset description'))
                    ]

        @staticmethod
        def get_response_body_api():
            return SharedDataSetSerializers.Operate.get_response_body_api()

    class Operate(ApiMixin, serializers.Serializer):
        id = serializers.CharField(required=True, error_messages=ErrMessage.char(
            _('dataset id')))
        user_id = serializers.UUIDField(required=False, error_messages=ErrMessage.char(
            _('user id')))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            if not QuerySet(DataSet).filter(id=self.data.get("id")).exists():
                raise AppApiException(300, _('id does not exist'))

        def list_application(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            dataset = QuerySet(DataSet).get(id=self.data.get("id"))
            
            # 检查用户是否为管理员
            from users.models import User
            from common.constants.permission_constants import RoleConstants
            try:
                current_user = User.objects.get(id=self.data.get("user_id"))
                is_admin = current_user.role == RoleConstants.ADMIN.name
            except User.DoesNotExist:
                is_admin = False
            
            # 管理员有查看所有应用的权限
            if is_admin:
                return select_list(get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset_application.sql')),
                    [str(dataset.user_id),  # 查询数据集所有者的个人应用
                     dataset.user_id,      # 查询数据集所有者所在团队的team_id
                     str(dataset.user_id)])  # 查询数据集所有者的团队成员关系
            
            # 普通用户的权限检查逻辑
            # 获取所有匹配的共享权限记录
            dataset_share_permissions = QuerySet(DatasetShare).filter(
                shared_with_id=self.data.get("user_id")
            )
            permissions = []
            # 如果存在共享权限记录，返回所有权限列表
            if dataset_share_permissions.exists():
                permissions = [share.permission for share in dataset_share_permissions]
            
            # 如果没有共享权限记录，继续执行原有的应用列表查询
            return select_list(get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset_application.sql')),
                [self.data.get('user_id') if self.data.get('user_id') == str(dataset.user_id) or (permissions and any(p is not None for p in permissions)) else None,
                 dataset.user_id, self.data.get('user_id')])

        def one(self, user_id, with_valid=True):
            if with_valid:
                self.is_valid()
            
            # 检查用户是否为管理员
            from users.models import User
            from common.constants.permission_constants import RoleConstants
            try:
                current_user = User.objects.get(id=user_id)
                is_admin = current_user.role == RoleConstants.ADMIN.name
            except User.DoesNotExist:
                is_admin = False
            
            # 根据用户角色设置查询条件
            if is_admin:
                # 管理员可以查看所有知识库的详情
                dataset_custom_sql = QuerySet(model=get_dynamics_model(
                    {'dataset.is_deleted': models.BooleanField()})).filter(
                    **{'dataset.is_deleted': False}
                )
                
                # 管理员查看时，为了获取完整的权限信息，需要查询目标知识库的实际所有者
                target_dataset = QuerySet(DataSet).filter(id=self.data.get("id")).first()
                if target_dataset:
                    target_user_id = str(target_dataset.user_id)
                else:
                    target_user_id = user_id  # 如果找不到数据集，回退到当前用户
                
                # 为管理员设置权限查询，查询目标知识库的实际权限关系
                team_member_permission_custom_sql = QuerySet(
                    model=get_dynamics_model({'user_id': models.CharField(),
                                            'team_member_permission.operate': ArrayField(
                                                verbose_name=_('permission'),
                                                base_field=models.CharField(max_length=256,
                                                                            blank=True,
                                                                            choices=AuthOperate.choices,
                                                                            default=AuthOperate.USE)
                                            )})).filter(
                    **{'user_id': target_user_id, 'team_member_permission.operate__contains': ['USE']}
                )
                
                datasetshare_custom_sql = QuerySet(
                    model=get_dynamics_model({'shared_with_id': models.CharField(),
                                            'permission': models.CharField()})).filter(
                    **{'shared_with_id': target_user_id, 
                    'permission__in': ['WRITE', 'READ', 'MANAGE']}
                )
            else:
                # 普通用户只能查看自己的知识库详情
                dataset_custom_sql = QuerySet(model=get_dynamics_model(
                    {'dataset.user_id': models.CharField()})).filter(
                    **{'dataset.user_id': user_id}
                )
                
                team_member_permission_custom_sql = QuerySet(
                    model=get_dynamics_model({'user_id': models.CharField(),
                                            'team_member_permission.operate': ArrayField(
                                                verbose_name=_('permission'),
                                                base_field=models.CharField(max_length=256,
                                                                            blank=True,
                                                                            choices=AuthOperate.choices,
                                                                            default=AuthOperate.USE)
                                            )})).filter(
                    **{'user_id': user_id, 'team_member_permission.operate__contains': ['USE']}
                )
                
                datasetshare_custom_sql = QuerySet(
                    model=get_dynamics_model({'shared_with_id': models.CharField(),
                                            'permission': models.CharField()})).filter(
                    **{'shared_with_id': user_id, 
                    'permission__in': ['WRITE', 'READ', 'MANAGE']}
                )
            
            query_set_dict = {
                'default_sql': QuerySet(model=get_dynamics_model(
                    {'temp.id': models.UUIDField()})).filter(**{'temp.id': self.data.get("id")}),
                            
                'dataset_custom_sql': dataset_custom_sql, 
                'team_member_permission_custom_sql': team_member_permission_custom_sql,
                'datasetshare_custom_sql': datasetshare_custom_sql
            }
            
            all_application_list = [str(adm.get('id')) for adm in self.list_application(with_valid=False)]
            
            return {
                **native_search(query_set_dict, select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset_share.sql')), with_search_one=True),
                'application_id_list': list(
                    filter(lambda application_id: all_application_list.__contains__(application_id),
                        [str(application_dataset_mapping.application_id) for
                            application_dataset_mapping in
                            QuerySet(ApplicationDatasetMapping).filter(
                                dataset_id=self.data.get('id'))])
                )
            }

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title=_('dataset name'),
                                           description=_('dataset name')),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title=_('dataset description'),
                                           description=_('dataset description')),
                    'meta': openapi.Schema(type=openapi.TYPE_OBJECT, title=_('meta'),
                                           description=_(
                                               'Knowledge base metadata->web:{source_url:xxx,selector:\'xxx\'},base:{}')),
                    'application_id_list': openapi.Schema(type=openapi.TYPE_ARRAY, title=_('application id list'),
                                                          description=_('application id list'),
                                                          items=openapi.Schema(type=openapi.TYPE_STRING))
                }
            )

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'name', 'desc', 'user_id', 'char_length', 'document_count',
                          'update_time', 'create_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                         description="id", default="xx"),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title=_('dataset name'),
                                           description=_('dataset name'), default=_('dataset name')),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title=_('dataset description'),
                                           description=_('dataset description'), default=_('dataset description')),
                    'user_id': openapi.Schema(type=openapi.TYPE_STRING, title=_('user id'),
                                              description=_('user id'), default="user_xxxx"),
                    'char_length': openapi.Schema(type=openapi.TYPE_STRING, title=_('char length'),
                                                  description=_('char length'), default=10),
                    'document_count': openapi.Schema(type=openapi.TYPE_STRING, title=_('document count'),
                                                     description=_('document count'), default=1),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('update time'),
                                                  description=_('update time'),
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('create time'),
                                                  description=_('create time'),
                                                  default="1970-01-01 00:00:00"
                                                  )
                }
            )

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('dataset id')),
                    ]