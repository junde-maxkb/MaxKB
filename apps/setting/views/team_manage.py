# coding=utf-8
"""
    @project: maxkb
    @Author：guofenggang
    @file： Team.py
    @date：2025/5/14 17:13
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
from setting.serializers.team_manage_serializers import TeamMemberSerializer, TeamSerializer, \
    get_page_response_body_api, get_page_request_params_api
from django.utils.translation import gettext_lazy as _

from setting.views.common import get_member_operation_object


class TeamMember(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Add member'),
                         operation_id=_('Add member'),
                         request_body=TeamMemberSerializer().get_request_body_api(),
                         tags=[_('Team Manager')])
    @has_permissions(PermissionConstants.TEAM_CREATE)
    @log(menu='Team Manager', operate='Add member',
         get_operation_object=lambda r, k: {'username_or_email': r.data.get('username_or_email')})
    def post(self, request: Request):
        user_id = request.user.id
        serializer = TeamMemberSerializer(data=request.data)
        return result.success(serializer.add_member(user_id, **request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_('Remove member'),
                             operation_id=_('Remove member'),
                             manual_parameters=TeamMemberSerializer.Operate.get_request_params_api(),
                             tags=[_('Team Manager')]
                             )
        @has_permissions(PermissionConstants.TEAM_DELETE)
        @log(menu='Team Manager', operate='Remove Team member',
             get_operation_object=lambda r, k: get_member_operation_object(k.get('member_id')))
        def delete(self, request: Request, member_id: str):
            return result.success(TeamMemberSerializer().Operate(
                data={'member_id': member_id, 'user_id': request.user.id}).delete())

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Add Team'),
                             operation_id=_('Add Team'),
                             request_body=TeamMemberSerializer().get_set_admin_request_body_api(),
                             tags=[_('Team Manager')])
        @has_permissions(PermissionConstants.TEAM_CREATE)
        @log(menu='Team Manager', operate='Add Team',
             get_operation_object=lambda r, k: {'member_id': r.data.get('member_id')})
        def post(self, request: Request, member_id):
            return result.success(TeamMemberSerializer().Operate(
                data={'member_id': member_id,
                      'user_id': request.user.id,
                      "is_manager": request.data.get("is_manager")
                      }).set_team_manager())


class Team(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('Get a list of team'),
                         operation_id=_('Get a list of team'),
                         responses=result.get_api_response(TeamSerializer().get_response_body_api()),
                         tags=[_('Team Manager')])
    @has_permissions(PermissionConstants.TEAM_READ)
    def get(self, request: Request):
        user_id = request.user.id
        return result.success(TeamSerializer().get_team_list(user_id, with_valid=False))

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Add Team'),
                         operation_id=_('Add Team'),
                         request_body=TeamSerializer().get_request_body_api(),
                         tags=[_('Team Manager')])
    @has_permissions(PermissionConstants.TEAM_CREATE)
    @log(menu='Team Manager', operate='Add Team',
         get_operation_object=lambda r, k: {'team_name': r.data[0] if r.data else ''})
    def post(self, request: Request):
        user_id = request.user.id
        # request.data is a list of team names
        team_names = request.data if isinstance(request.data, list) else [request.data]
        serializer = TeamSerializer(data={'team_names': team_names})
        return result.success(serializer.add_team(user_id, team_names))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Update team name'),
                             operation_id=_('Update team name'),
                             request_body=TeamSerializer().Operate.get_request_body_api(),
                             manual_parameters=TeamSerializer.Operate.get_request_params_api(),
                             tags=[_('Team Manager')]
                             )
        @has_permissions(PermissionConstants.TEAM_EDIT)
        @log(menu='Team Manager', operate='Update team name',
             get_operation_object=lambda r, k: get_member_operation_object(k.get('team_name'))
             )
        def put(self, request: Request, team_id: str):
            user_id = request.user.id
            return result.success(TeamSerializer.Operate(
                data={'team_id': team_id, "team_name": request.data.get("team_name")}).edit(user_id))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_('Remove Team'),
                             operation_id=_('Remove Team'),
                             manual_parameters=TeamSerializer.Operate.get_request_params_api(),
                             tags=[_('Team Manager')]
                             )
        @has_permissions(PermissionConstants.TEAM_DELETE)
        @log(menu='Team', operate='Remove Team',
             get_operation_object=lambda r, k: get_member_operation_object(k.get('team_id')))
        def delete(self, request: Request, team_id: str):
            user_id = request.user.id
            return result.success(TeamSerializer.Operate(
                data={'team_id': team_id}).delete(user_id))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @swagger_auto_schema(operation_summary=_("Get the list of application versions by page"),
                             operation_id=_("Get the list of application versions by page"),
                             manual_parameters=get_page_request_params_api(),
                             responses=get_page_response_body_api(),
                             tags=[_('TeamManager')])
        @action(methods=['GET'], detail=False)
        @has_permissions(PermissionConstants.TEAM_READ)
        def get(self, request: Request, team_id, current_page, page_size):
            d = TeamMemberSerializer.Query(
                data={'email_or_username': request.query_params.get('email_or_username', None),
                      'team_id': team_id})
            return result.success(d.page(current_page, page_size))
