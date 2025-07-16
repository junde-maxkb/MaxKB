# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： dataset.py
    @date：2023/9/21 15:52
    @desc:
"""

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.views import Request

import dataset.models
from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import PermissionConstants, CompareConstants, Permission, Group, Operate, \
    ViewPermission, RoleConstants
from common.log.log import log
from common.response import result
from common.response.result import get_page_request_params, get_page_api_response, get_api_response
from common.swagger_api.common_api import CommonApi
from dataset.serializers.common_serializers import GenerateRelatedSerializer
from dataset.serializers.dataset_serializers import DataSetSerializers
from dataset.views.common import get_dataset_operation_object
from setting.serializers.provider_serializers import ModelSerializer
from django.utils.translation import gettext_lazy as _
from dataset.models.data_set import DataSet, DatasetShare
from users.models import User
from django.db.models import Q


class Dataset(APIView):
    authentication_classes = [TokenAuth]

    class SyncWeb(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_("Synchronize the knowledge base of the website"),
                             operation_id=_("Synchronize the knowledge base of the website"),
                             manual_parameters=DataSetSerializers.SyncWeb.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base')])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('dataset_id'))],
            compare=CompareConstants.AND), PermissionConstants.DATASET_EDIT,
            compare=CompareConstants.AND)
        @log(menu='Knowledge Base', operate="Synchronize the knowledge base of the website",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            return result.success(DataSetSerializers.SyncWeb(
                data={'sync_type': request.query_params.get('sync_type'), 'id': dataset_id,
                      'user_id': str(request.user.id)}).sync())

    class CreateQADataset(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_("Create QA knowledge base"),
                             operation_id=_("Create QA knowledge base"),
                             manual_parameters=DataSetSerializers.Create.CreateQASerializers.get_request_params_api(),
                             responses=get_api_response(
                                 DataSetSerializers.Create.CreateQASerializers.get_response_body_api()),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(PermissionConstants.DATASET_CREATE, compare=CompareConstants.AND)
        @log(menu='Knowledge Base', operate="Create QA knowledge base",
             get_operation_object=lambda r, keywords: {'name': r.data.get('name'), 'desc': r.data.get('desc'),
                                                       'file_list': r.FILES.getlist('file')})
        def post(self, request: Request):
            return result.success(DataSetSerializers.Create(data={'user_id': request.user.id}).save_qa({
                'file_list': request.FILES.getlist('file'),
                'name': request.data.get('name'),
                'desc': request.data.get('desc')
            }))

    class CreateWebDataset(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Create a web site knowledge base'),
                             operation_id=_('Create a web site knowledge base'),
                             request_body=DataSetSerializers.Create.CreateWebSerializers.get_request_body_api(),
                             responses=get_api_response(
                                 DataSetSerializers.Create.CreateWebSerializers.get_response_body_api()),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(PermissionConstants.DATASET_CREATE, compare=CompareConstants.AND)
        @log(menu='Knowledge Base', operate="Create a web site knowledge base",
             get_operation_object=lambda r, keywords: {'name': r.data.get('name'), 'desc': r.data.get('desc'),
                                                       'file_list': r.FILES.getlist('file'),
                                                       'meta': {'source_url': r.data.get('source_url'),
                                                                'selector': r.data.get('selector'),
                                                                'embedding_mode_id': r.data.get('embedding_mode_id')}}
             )
        def post(self, request: Request):
            return result.success(DataSetSerializers.Create(data={'user_id': request.user.id}).save_web(request.data))

    class Application(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get a list of applications available in the knowledge base'),
                             operation_id=_('Get a list of applications available in the knowledge base'),
                             manual_parameters=DataSetSerializers.Application.get_request_params_api(),
                             responses=result.get_api_array_response(
                                 DataSetSerializers.Application.get_response_body_api()),
                             tags=[_('Knowledge Base')])
        def get(self, request: Request, dataset_id: str):
            return result.success(DataSetSerializers.Operate(
                data={'id': dataset_id, 'user_id': str(request.user.id)}).list_application())

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('Get a list of knowledge bases'),
                         operation_id=_('Get a list of knowledge bases'),
                         manual_parameters=DataSetSerializers.Query.get_request_params_api(),
                         responses=result.get_api_array_response(DataSetSerializers.Query.get_response_body_api()),
                         tags=[_('Knowledge Base')])
    @has_permissions(PermissionConstants.DATASET_READ, compare=CompareConstants.AND)
    def get(self, request: Request):
        data = {key: str(value) for key, value in request.query_params.items()}
        d = DataSetSerializers.Query(data={**data, 'user_id': str(request.user.id)})
        d.is_valid()
        return result.success(d.list())

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Create a knowledge base'),
                         operation_id=_('Create a knowledge base'),
                         request_body=DataSetSerializers.Create.get_request_body_api(),
                         responses=get_api_response(DataSetSerializers.Create.get_response_body_api()),
                         tags=[_('Knowledge Base')]
                         )
    @has_permissions(PermissionConstants.DATASET_CREATE, compare=CompareConstants.AND)
    @log(menu='Knowledge Base', operate="Create a knowledge base",
         get_operation_object=lambda r, keywords: {'name': r.data.get('name'), 'desc': r.data.get('desc')})
    def post(self, request: Request):
        return result.success(DataSetSerializers.Create(data={'user_id': request.user.id}).save(request.data))

    class HitTest(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary=_('Hit test list'), operation_id=_('Hit test list'),
                             manual_parameters=CommonApi.HitTestApi.get_request_params_api(),
                             responses=result.get_api_array_response(CommonApi.HitTestApi.get_response_body_api()),
                             tags=[_('Knowledge Base')])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.USE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        def get(self, request: Request, dataset_id: str):
            return result.success(
                DataSetSerializers.HitTest(data={'id': dataset_id, 'user_id': request.user.id,
                                                 "query_text": request.query_params.get("query_text"),
                                                 "top_number": request.query_params.get("top_number"),
                                                 'similarity': request.query_params.get('similarity'),
                                                 'search_mode': request.query_params.get('search_mode')}).hit_test(
                ))

    class Embedding(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="PUT", detail=False)
        @swagger_auto_schema(operation_summary=_('Re-vectorize'), operation_id=_('Re-vectorize'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        @log(menu='Knowledge Base', operate="Re-vectorize",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            return result.success(
                DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).re_embedding())

    class GenerateRelated(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Generate related'), operation_id=_('Generate related'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             request_body=GenerateRelatedSerializer.get_request_body_api(),
                             tags=[_('Knowledge Base')]
                             )
        @log(menu='document', operate="Generate related documents",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id'))
             )
        def put(self, request: Request, dataset_id: str):
            return result.success(
                DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).generate_related(
                    request.data))

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary=_('Export knowledge base'), operation_id=_('Export knowledge base'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        @log(menu='Knowledge Base', operate="Export knowledge base",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def get(self, request: Request, dataset_id: str):
            return DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).export_excel()

    class ExportZip(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary=_('Export knowledge base containing images'),
                             operation_id=_('Export knowledge base containing images'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        @log(menu='Knowledge Base', operate="Export knowledge base containing images",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def get(self, request: Request, dataset_id: str):
            return DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).export_zip()

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="DELETE", detail=False)
        @swagger_auto_schema(operation_summary=_('Delete knowledge base'), operation_id=_('Delete knowledge base'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base')])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')),
                         lambda r, k: Permission(group=Group.DATASET, operate=Operate.DELETE,
                                                 dynamic_tag=k.get('dataset_id')), compare=CompareConstants.AND)
        @log(menu='Knowledge Base', operate="Delete knowledge base",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str):
            operate = DataSetSerializers.Operate(data={'id': dataset_id})
            return result.success(operate.delete())





        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary=_('Query knowledge base details based on knowledge base id'),
                             operation_id=_('Query knowledge base details based on knowledge base id'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=get_api_response(DataSetSerializers.Operate.get_response_body_api()),
                             tags=[_('Knowledge Base')])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.USE,
                                                        dynamic_tag=keywords.get('dataset_id')),dataset_permission='WRITE')
        def get(self, request: Request, dataset_id: str):
            print(f"正在获取知识库详情, 知识库ID: {dataset_id}, 用户ID: {request.user.id}")
            data = DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).one(
                user_id=request.user.id)
            print(f"获取知识库详情成功: {data}")
            return result.success(data)

        @action(methods="PUT", detail=False)
        @swagger_auto_schema(operation_summary=_('Modify knowledge base information'),
                             operation_id=_('Modify knowledge base information'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             request_body=DataSetSerializers.Operate.get_request_body_api(),
                             responses=get_api_response(DataSetSerializers.Operate.get_response_body_api()),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        @log(menu='Knowledge Base', operate="Modify knowledge base information",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            return result.success(
                DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).edit(request.data,
                                                                                                     user_id=request.user.id))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get the knowledge base paginated list'),
                             operation_id=_('Get the knowledge base paginated list'),
                             manual_parameters=get_page_request_params(
                                 DataSetSerializers.Query.get_request_params_api()),
                             responses=get_page_api_response(DataSetSerializers.Query.get_response_body_api()),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(PermissionConstants.DATASET_READ, compare=CompareConstants.AND)
        def get(self, request: Request, current_page, page_size):
            d = DataSetSerializers.Query(
                data={'name': request.query_params.get('name', None), 'desc': request.query_params.get("desc", None),
                      'user_id': str(request.user.id),
                      'select_user_id': request.query_params.get('select_user_id', None)})
            d.is_valid()
            return result.success(d.page(current_page, page_size))

    class Model(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('dataset_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, dataset_id: str):
            return result.success(
                ModelSerializer.Query(
                    data={'user_id': request.user.id, 'model_type': 'LLM'}).list(
                    with_valid=True)
            )

    class DatasetMembers(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @swagger_auto_schema(operation_summary=_('获取知识库团队成员及其权限'),
                             operation_id=_('获取知识库团队成员及其权限'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=get_api_response({
                                 'type': 'object',
                                 'properties': {
                                     'dataset_id': {'type': 'string'},
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
                             tags=[_('Knowledge Base')])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        def get(self, request: Request, dataset_id: str):
            from setting.models.team_management import TeamMember, TeamMemberPermission
            from django.db.models import Q
            from setting.models.team_management import Team
            # # 获取团队成员
            # team_members = TeamMember.objects.filter(
            #     # Q(team__user_id=request.user.id) | Q(user_id=request.user.id)
            # ).distinct()
            ignore_user_ids = []
            # 查询知识库所有者ID
            # ignore_user_ids.append(DataSet.objects.get(id=dataset_id).user_id)
            # ignore_user_ids.append(request.user.id)

            dataset_share = DatasetShare.objects.filter(
                dataset_id_id=dataset_id,
                shared_with_type='USER'
            ).exclude(
                shared_with_id__in=ignore_user_ids
            ).select_related('dataset_id')
            dataset_share_team = DatasetShare.objects.filter(
                dataset_id_id=dataset_id,
                shared_with_type='TEAM'
            ).select_related('dataset_id')
            
            # 获取每个成员对当前知识库的权限
            members_with_permissions = []
            for share in dataset_share:
                user = User.objects.get(id=share.shared_with_id)
                
                members_with_permissions.append({
                    'user_id': str(share.shared_with_id),
                    'type': 'USER',
                    'username': user.username,
                    'permission': share.permission if share.permission else 'NONE'
                })
            for share in dataset_share_team:
                Team = Team.objects.get(id=share.shared_with_id)
                
                members_with_permissions.append({
                    'user_id': str(share.shared_with_id),
                    'type': 'TEAM',
                    'username': Team.name,
                    'permission': share.permission if share.permission else 'NONE'
                })
                
            
            return result.success({
                'dataset_id': dataset_id,
                'members': members_with_permissions
            })

    class PutMemberPermissions(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["PUT"], detail=False)
        @swagger_auto_schema(operation_summary=_('更新数据集分享权限'),
                             operation_id=_('更新数据集分享权限'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             request_body={
                                 'type': 'object',
                                 'properties': {
                                     'user_id': {'type': 'string', 'description': '用户ID'},
                                     'permission': {'type': 'string', 'description': '权限类型'}
                                 },
                                 'required': ['user_id', 'permission']
                             },
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base')])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')),dataset_permission='MANAGE')
        @log(menu='Knowledge Base', operate="更新数据集分享权限",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            from dataset.models.data_set import DatasetShare
            from django.utils import timezone
            from setting.models.team_management import TeamMember
            user_id = request.data.get('user_id')
            permission = request.data.get('permission') if request.data.get('permission') else 'NONE'
            share_with_type = request.data.get('share_with_type')
            
            # 检查数据集是否存在
            dataset = DataSet.objects.filter(id=dataset_id).first()
            if not dataset:
                return result.error(_('数据集不存在'))
            
            if share_with_type == "USER":
                # 查找或创建分享记录
                share_record, created = DatasetShare.objects.get_or_create(
                    dataset_id_id=dataset.id,
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
                print(f"团队ID: {team_id}")
                # 查找或创建团队分享记录
                share_record, created = DatasetShare.objects.get_or_create(
                    dataset_id_id=dataset.id,
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
        @swagger_auto_schema(operation_summary=_('获取共享给我的知识库分页列表'),
                             operation_id=_('获取共享给我的知识库分页列表'),
                             manual_parameters=DataSetSerializers.SharePageQuery.get_request_params_api(),
                             responses=get_page_api_response(DataSetSerializers.SharePageQuery.get_response_body_api()),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(PermissionConstants.DATASET_READ, compare=CompareConstants.AND)
        def get(self, request: Request, current_page, page_size):
            from setting.models.team_management import TeamMember
            from users.models import User
            # 1. 获取共享给我的知识库ID列表及权限
            user_teams = TeamMember.objects.filter(Q(user_id=request.user.id) | Q(team_id=request.user.id)).values_list('team_id', flat=True)
            
            # 分别获取团队共享和用户共享的数据集，并预先加载关联
            team_shared_datasets = DatasetShare.objects.filter(
                shared_with_type='TEAM',
                shared_with_id__in=[str(team_id) for team_id in user_teams]
            ).exclude(permission='NONE').select_related('dataset_id')
            
            user_shared_datasets = DatasetShare.objects.filter(
                shared_with_type='USER',
                shared_with_id=str(request.user.id)
            ).exclude(permission='NONE').select_related('dataset_id')
            
            # 合并两个查询集
            shared_datasets = list(team_shared_datasets) + list(user_shared_datasets)

            # 如果没有共享的数据集，直接返回空结果
            if not shared_datasets:
                return result.success({
                    'records': [],
                    'total': 0,
                    'page': current_page,
                    'page_size': page_size
                })
            
            # 2. 构建查询参数
            query_params = {
                'name': request.query_params.get('name', None),
                'desc': request.query_params.get("desc", None),
                'user_id': str(request.user.id),
                'dataset_ids': [str(share.dataset_id_id) for share in shared_datasets]
            }
            
            # 3. 使用SharePageQuery获取知识库列表
            d = DataSetSerializers.SharePageQuery(data=query_params)
            d.is_valid()
            result_data = d.page(current_page, page_size)
            
            # 4. 为每个知识库添加权限信息和创建人信息
            permission_map = {str(share.dataset_id_id): share.permission for share in shared_datasets}
            
            # 获取所有知识库的创建人信息
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
        @swagger_auto_schema(operation_summary=_('退出共享知识库'),
                             operation_id=_('退出共享知识库'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base')])
        def put(self, request: Request, dataset_id: str):
            from setting.models.team_management import TeamMember
            from dataset.models.data_set import DatasetShare

            # 获取用户所在的团队
            user_teams = TeamMember.objects.filter(user_id=request.user.id).values_list('team_id', flat=True)
            
            # 检查团队共享
            team_share = DatasetShare.objects.filter(
                dataset_id_id=dataset_id,
                shared_with_type='TEAM',
                shared_with_id__in=[str(team_id) for team_id in user_teams]
            ).exclude(permission='NONE').exists()
            
            # 检查个人共享
            user_share = DatasetShare.objects.filter(
                dataset_id_id=dataset_id,
                shared_with_type='USER',
                shared_with_id=str(request.user.id)
            ).exclude(permission='NONE').exists()
            
            # 如果只有团队共享，不允许退出
            if team_share and not user_share:
                return result.error(_('该知识库是通过团队共享的，无法退出'))
            
            # 如果有个人共享，将个人权限设置为NONE
            if user_share:
                DatasetShare.objects.filter(
                    dataset_id_id=dataset_id,
                    shared_with_type='USER',
                    shared_with_id=str(request.user.id)
                ).update(permission='NONE')
            
            return result.success({'message': '成功退出共享知识库'})

    class OrganizationPage(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('获取机构知识库分页列表'),
                             operation_id=_('获取机构知识库分页列表'),
                             manual_parameters=DataSetSerializers.OrganizationPageQuery.get_request_params_api(),
                             responses=get_page_api_response(DataSetSerializers.OrganizationPageQuery.get_response_body_api()),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(PermissionConstants.DATASET_READ, compare=CompareConstants.AND)
        def get(self, request: Request, current_page, page_size):
            from dataset.models.data_set import OrganizationDataset
            from users.models import User
            
            # 获取所有机构知识库ID
            dataset_ids = list(OrganizationDataset.objects.filter().values_list('dataset_id', flat=True))
            print(f"机构知识库ID列表: {dataset_ids}")  # 打印机构知识库ID列表
            
            # 构建查询参数
            query_params = {
                'name': request.query_params.get('name', None),
                'desc': request.query_params.get("desc", None),
                'dataset_ids': dataset_ids  # 直接传递dataset_ids列表
            }
            
            # 使用OrganizationPageQuery获取知识库列表
            d = DataSetSerializers.OrganizationPageQuery(data=query_params)
            d.is_valid()
            result_data = d.page(current_page, page_size)
            
            # 获取所有知识库的创建人信息
            creator_ids = [item['user_id'] for item in result_data['list']]
            creators = {str(user.id): user.username for user in User.objects.filter(id__in=creator_ids)}
            
            # 为每个知识库添加创建人信息
            for item in result_data['list']:
                item['creator_name'] = creators.get(str(item['user_id']), '')
            
            # 修改返回数据结构
            return result.success({
                'records': result_data['list'],
                'total': result_data['total'],
                'page': result_data['page'],
                'page_size': result_data['page_size']
            })

    class AddToOrganization(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["POST"], detail=False)
        @swagger_auto_schema(operation_summary=_('将知识库添加到机构知识库'),
                             operation_id=_('将知识库添加到机构知识库'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base')])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        @log(menu='Knowledge Base', operate="将知识库添加到机构知识库",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def post(self, request: Request, dataset_id: str):
            from dataset.models.data_set import OrganizationDataset, DataSet
            
            # 检查知识库是否存在
            dataset = DataSet.objects.filter(id=dataset_id).first()
            if not dataset:
                return result.error(_('知识库不存在'))
            
            # 检查是否已经是机构知识库
            if OrganizationDataset.objects.filter(dataset_id=dataset_id).exists():
                return result.error(_('该知识库已经是机构知识库'))
            
            # 创建机构知识库记录
            OrganizationDataset.objects.create(dataset_id=dataset_id)
            
            return result.success({'message': '成功将知识库添加到机构知识库'})

    class RemoveFromOrganization(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["POST"], detail=False)
        @swagger_auto_schema(operation_summary=_('将知识库从机构知识库中移除'),
                             operation_id=_('将知识库从机构知识库中移除'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base')])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        @log(menu='Knowledge Base', operate="将知识库从机构知识库中移除",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def post(self, request: Request, dataset_id: str):
            from dataset.models.data_set import OrganizationDataset, DataSet
            
            # 检查知识库是否存在
            dataset = DataSet.objects.filter(id=dataset_id).first()
            if not dataset:
                return result.error(_('知识库不存在'))
            
            # 检查是否是机构知识库
            org_dataset = OrganizationDataset.objects.filter(dataset_id=dataset_id).first()
            if not org_dataset:
                return result.error(_('该知识库不是机构知识库'))
            
            # 删除机构知识库记录
            org_dataset.delete()
            
            return result.success({'message': '成功将知识库从机构知识库中移除'})

    class RecycleBinPage(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('获取回收站知识库分页列表'),
                             operation_id=_('获取回收站知识库分页列表'),
                             manual_parameters=DataSetSerializers.RecycleBinQuery.get_request_params_api(),
                             responses=get_page_api_response(DataSetSerializers.RecycleBinQuery.get_response_body_api()),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(PermissionConstants.DATASET_READ, compare=CompareConstants.AND)
        def get(self, request: Request, current_page, page_size):
            from users.models import User
            
            # 构建查询参数（去掉user_id，显示所有已删除的知识库）
            query_params = {
                'name': request.query_params.get('name', None),
                'desc': request.query_params.get("desc", None),
                'user_id': ''  # 空值，不再按用户过滤
            }
            
            # 使用RecycleBinQuery获取知识库列表
            d = DataSetSerializers.RecycleBinQuery(data=query_params)
            d.is_valid()
            result_data = d.page(current_page, page_size)
            
            # 获取所有知识库的创建人信息
            creator_ids = [item['user_id'] for item in result_data['list']]
            creators = {str(user.id): user.username for user in User.objects.filter(id__in=creator_ids)}
            
            # 为每个知识库添加创建人信息
            for item in result_data['list']:
                item['creator_name'] = creators.get(str(item['user_id']), '')
            
            # 修改返回数据结构
            return result.success({
                'records': result_data['list'],
                'total': result_data['total'],
                'page': result_data['page'],
                'page_size': result_data['page_size']
            })

    class Restore(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["PUT"], detail=False)
        @swagger_auto_schema(operation_summary=_('恢复已删除的知识库'),
                             operation_id=_('恢复已删除的知识库'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base')])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        @log(menu='Knowledge Base', operate="恢复已删除的知识库",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            operate = DataSetSerializers.Operate(data={'id': dataset_id})
            return result.success(operate.restore())

    class PermanentlyDelete(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["DELETE"], detail=False)
        @swagger_auto_schema(operation_summary=_('永久删除知识库'),
                             operation_id=_('永久删除知识库'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base')])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        @log(menu='Knowledge Base', operate="永久删除知识库",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str):
            operate = DataSetSerializers.Operate(data={'id': dataset_id})
            return result.success(operate.permanently_delete())