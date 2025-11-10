# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： Team.py
    @date：2023/9/25 17:13
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
from setting.serializers.team_serializers import TeamMemberSerializer, get_response_body_api, \
    UpdateTeamMemberPermissionSerializer
from django.utils.translation import gettext_lazy as _

from setting.views.common import get_member_operation_object, get_member_operation_object_batch
from users.models import User


class UserTeams(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('获取当前用户所在的所有团队'),
                         operation_id=_('获取当前用户所在的所有团队'),
                         responses=result.get_api_response(get_response_body_api()),
                         tags=[_('Team')])
    @has_permissions(PermissionConstants.TEAM_READ)
    def get(self, request: Request):
        from setting.models.team_management import Team, TeamMember
        from django.db.models import Q

        # 获取用户作为管理员的团队
        managed_team = TeamMember.objects.filter(user_id=request.user.id, is_manager=True).select_related(
            'team').values(
            'team_id', 'team__name'
        )

        # 获取用户作为成员的团队
        member_teams = TeamMember.objects.filter(user_id=request.user.id, is_manager=False).select_related(
            'team').values(
            'team_id', 'team__name'
        )
        print(request.user)
        print(managed_team)
        print(member_teams)

        # 合并结果
        teams = []
        for team in managed_team:
            teams.append({
                'id': str(team['team_id']),
                'name': team['team__name'],
                'role': 'manager'
            })

        for team in member_teams:
            teams.append({
                'id': str(team['team_id']),
                'name': team['team__name'],
                'role': 'member'
            })

        return result.success(teams)


class TeamMember(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('获取当前用户所在的所有团队'),
                         operation_id=_('获取当前用户所在的所有团队'),
                         responses=result.get_api_response(get_response_body_api()),
                         tags=[_('Team')])
    @has_permissions(PermissionConstants.TEAM_READ)
    def get_user_teams(self, request: Request):
        from setting.models.team_management import Team, TeamMember
        from django.db.models import Q
        print(request.user.id)
        print("调试信息: 用户ID", request.user.id)

        # 获取用户作为管理员的团队
        managed_teams = TeamMember.objects.filter(user_id=request.user.id, is_manager=True).select_related(
            'team').values(
            'team_id', 'team__name', 'team__user_id'
        )
        print("调试信息: 管理的团队", managed_teams)

        # 获取用户作为成员的团队
        member_teams = TeamMember.objects.filter(user_id=request.user.id).select_related('team').values(
            'team_id', 'team__name', 'team__user_id'
        )
        print("调试信息: 成员的团队", member_teams)

        # 合并结果
        teams = []
        for team in managed_teams:
            teams.append({
                'id': str(team['team_id']),
                'name': team['team__name'],
                'user_id': str(team['team__id']),
                'role': 'manager'
            })

        for team in member_teams:
            teams.append({
                'id': str(team['team_id']),
                'name': team['team__name'],
                'user_id': str(team['team__id']),
                'role': 'member'
            })

        print("调试信息: 最终团队列表", teams)
        return result.success(teams)

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('Get a list of team members'),
                         operation_id=_('Get a list of team members'),
                         responses=result.get_api_response(get_response_body_api()),
                         tags=[_('Team')])
    @has_permissions(PermissionConstants.TEAM_READ)
    def get(self, request: Request):
        return result.success(TeamMemberSerializer(data={'team_id': str(request.user.id)}).list_member())

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Add member'),
                         operation_id=_('Add member'),
                         request_body=TeamMemberSerializer().get_request_body_api(),
                         tags=[_('Team')])
    @has_permissions(PermissionConstants.TEAM_CREATE)
    @log(menu='Team', operate='Add member',
         get_operation_object=lambda r, k: {'name': r.data.get('username_or_email')})
    def post(self, request: Request):
        team = TeamMemberSerializer(data={'team_id': str(request.user.id)})
        return result.success((team.add_member(**request.data)))

    class Batch(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Add members in batches'),
                             operation_id=_('Add members in batches'),
                             request_body=TeamMemberSerializer.get_bach_request_body_api(),
                             tags=[_('Team')])
        @has_permissions(PermissionConstants.TEAM_CREATE)
        @log(menu='Team', operate='Add members in batches',
             get_operation_object=lambda r, k: get_member_operation_object_batch(r.data))
        def post(self, request: Request):
            return result.success(
                TeamMemberSerializer(data={'team_id': request.user.id}).batch_add_member(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get team member permissions'),
                             operation_id=_('Get team member permissions'),
                             manual_parameters=TeamMemberSerializer.Operate.get_request_params_api(),
                             tags=[_('Team')])
        @has_permissions(PermissionConstants.TEAM_READ)
        def get(self, request: Request, member_id: str):
            return result.success(TeamMemberSerializer.Operate(
                data={'member_id': member_id, 'team_id': str(request.user.id)}).list_member_permission())

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Update team member permissions'),
                             operation_id=_('Update team member permissions'),
                             request_body=UpdateTeamMemberPermissionSerializer().get_request_body_api(),
                             manual_parameters=TeamMemberSerializer.Operate.get_request_params_api(),
                             tags=[_('Team')]
                             )
        @has_permissions(PermissionConstants.TEAM_EDIT)
        @log(menu='Team', operate='Update team member permissions',
             get_operation_object=lambda r, k: get_member_operation_object(k.get('member_id'))
             )
        def put(self, request: Request, member_id: str):
            return result.success(TeamMemberSerializer.Operate(
                data={'member_id': member_id, 'team_id': str(request.user.id)}).edit(request.data))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_('Remove member'),
                             operation_id=_('Remove member'),
                             manual_parameters=TeamMemberSerializer.Operate.get_request_params_api(),
                             tags=[_('Team')]
                             )
        @has_permissions(PermissionConstants.TEAM_DELETE)
        @log(menu='Team', operate='Remove member',
             get_operation_object=lambda r, k: get_member_operation_object(k.get('member_id')))
        def delete(self, request: Request, member_id: str):
            return result.success(TeamMemberSerializer.Operate(
                data={'member_id': member_id, 'team_id': str(request.user.id)}).delete())


class ShareableList(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('获取可共享的用户和团队列表'),
                         operation_id=_('获取可共享的用户和团队列表'),
                         responses=result.get_api_response(get_response_body_api()),
                         tags=[_('Team')])
    @has_permissions(PermissionConstants.TEAM_READ)
    def get(self, request: Request):
        from setting.models.team_management import Team
        from django.db.models import Q

        keyword = request.query_params.get('keyword', '')

        # 获取所有团队（不限于用户所在团队）
        all_teams = Team.objects.all().values(
            'id',
            'name'
        )

        # 获取所有用户
        all_users = User.objects.filter(
            Q(nick_name__icontains=keyword) |
            Q(username__icontains=keyword),
            is_active=True
        ).values(
            'id',
            'username',
            'email',
        )

        # 构建返回结果
        shareable_list = {
            'teams': [],
            'users': []
        }

        # 添加所有用户信息
        for user in all_users:
            shareable_list['users'].append({
                'id': str(user['id']),
                'name': user['username'],
                'email': user['email'],
                'type': 'USER'
            })

        # 添加所有团队信息
        for team in all_teams:
            shareable_list['teams'].append({
                'id': str(team['id']),
                'name': team['name'],
                'type': 'TEAM'
            })

        return result.success(shareable_list)
