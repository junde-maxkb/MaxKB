# coding=utf-8
"""
    @project: maxkb
    @Author：guofenggang
    @file： Team.py
    @date：2025/5/14 17:13
    @desc:
"""

from django.core import cache
from django.db import transaction
from django.db.models import QuerySet, Q
from drf_yasg import openapi
from rest_framework import serializers

from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.response.result import get_api_response
from common.util.field_message import ErrMessage
from setting.models import TeamMember, Team
from users.models.user import User
from users.serializers.user_serializers import UserSerializer
from django.utils.translation import gettext_lazy as _

user_cache = cache.caches['user_cache']


def get_page_response_body_api():
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'email', 'id'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_STRING, title='ID', description="ID"),
            'team_id': openapi.Schema(type=openapi.TYPE_STRING, title='Team ID', description="Team ID"),
            'user_id': openapi.Schema(type=openapi.TYPE_STRING, title='User ID', description="User ID"),
            'team_member_type': openapi.Schema(type=openapi.TYPE_STRING, title=_("Team Member Type"),
                                               description=_("Team Member Type")),
            'username': openapi.Schema(type=openapi.TYPE_STRING, title=_("Username"),
                                       description=_("Username")),
            'email': openapi.Schema(type=openapi.TYPE_STRING, title=_("Email"), description=_("Email")),
            'is_manager': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("IsManager"), description=_("IsManager"))
        }
    )


def get_page_request_params_api():
    return [openapi.Parameter(name='email_or_username',
                              in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING,
                              required=True,
                              description=_("Email or username"))]


class TeamMemberSerializer(ApiMixin, serializers.Serializer):
    member_id = serializers.UUIDField(required=False, error_messages=ErrMessage.uuid(_('team id')))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['team_name'],
            properties={
                'team_name': openapi.Schema(type=openapi.TYPE_STRING, title=_('Team name'),
                                            description=_('Team name'))

            }
        )

    @staticmethod
    def get_set_admin_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['member_id', 'is_manager'],
            properties={
                'member_id': openapi.Schema(type=openapi.TYPE_STRING, title=_('Member id'),
                                            description=_('Member id')),
                'is_manager': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_('Ismanager'),
                                             description=_('Ismanager')),

            }
        )

    @staticmethod
    def get_response_body_api():
        return get_api_response(openapi.Schema(
            type=openapi.TYPE_ARRAY, title=_('member list'), description=_('member list'),
            items=UserSerializer().get_response_body_api()
        ))

    def add_member(self, user_id, team_id, username_or_email, with_valid=True):
        """
        添加一个团队成员
        :param with_valid: 是否校驗參數
        :param username_or_email: 添加成员的邮箱或者用户名
        :return: 成员列表
        """

        if with_valid:
            self.is_valid(raise_exception=True)
        user = User.objects.get(id=user_id)
        team = Team.objects.get(id=team_id)
        team_member = TeamMember.objects.filter(user=user, team=team).first()
        if user.role != "ADMIN" and not team_member.is_manager:
            raise AppApiException(403, _('Permission denied. Only admin or team manager can delete team.'))
        if username_or_email is None:
            raise AppApiException(500, _('Username or email is required'))
        user = QuerySet(User).filter(
            Q(username=username_or_email) | Q(email=username_or_email)).first()
        if user is None:
            raise AppApiException(500, _('User does not exist'))
        if QuerySet(TeamMember).filter(team_id=team_id, user_id=user.id):
            raise AppApiException(500, _('Team Member is already exist'))
        team = QuerySet(Team).get(id=team_id)
        TeamMember.objects.create(
            team=team,
            user=user,
            is_manager=False
        )
        return self.list_member(with_valid=False)

    class Query(ApiMixin, serializers.Serializer):
        email_or_username = serializers.CharField(required=False, allow_null=True,
                                                  error_messages=ErrMessage.char(_('Email or username')))
        team_id = serializers.CharField(required=True, allow_null=True,
                                        error_messages=ErrMessage.char(_('Team Id')))

        def get_query_set(self):
            email_or_username = self.data.get('email_or_username')
            query_set = TeamMember.objects.filter(team_id=self.data.get('team_id'))
            if email_or_username is not None:
                query_set = query_set.filter(
                    Q(user__username__contains=email_or_username) | Q(user__email__contains=email_or_username))
            query_set = query_set.order_by("-create_time")
            return query_set

        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return page_search(current_page, page_size,
                               self.get_query_set(),
                               post_records_handler=lambda u: TeamMemberInstanceSerializer(u).data)

    def list_member(self, with_valid=True):
        """
        获取 团队中的成员列表
        :return: 成员列表
        """
        if with_valid:
            self.is_valid(raise_exception=True)
        # 普通成員列表
        member_list = list(map(lambda t: {"id": t.id, 'email': t.user.email, 'username': t.user.username,
                                          'team_id': self.data.get("team_id"), 'user_id': t.user.id,
                                          'type': 'member'},
                               QuerySet(TeamMember).filter(team_id=self.data.get("team_id"))))
        return member_list

    class Operate(ApiMixin, serializers.Serializer):
        member_id = serializers.CharField(required=True, error_messages=ErrMessage.char(_('member id')))
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_('user id')))
        is_manager = serializers.BooleanField(required=False, error_messages=ErrMessage.char(_('is_manager')))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            member_id = self.data.get("member_id")
            user = User.objects.get(id=self.data.get("user_id"))
            team = TeamMember.objects.get(id=member_id).team
            team_member = TeamMember.objects.filter(user=user, team=team).first()
            if user.role != "ADMIN" and not team_member.is_manager:
                raise AppApiException(403, _('Permission denied. Only admin or team manager can delete team.'))
            return True

        def delete(self, with_valid=True):
            """
            删除团队成员
            :return:
            """
            if with_valid:
                self.is_valid(raise_exception=True)
            member_id = self.data.get("member_id")
            QuerySet(TeamMember).filter(id=member_id).delete()
            return True

        def set_team_manager(self, with_valid=True):
            """
            设置管理员
            :return:
            """
            if with_valid:
                self.is_valid(raise_exception=True)
            member_id = self.data.get("member_id")
            is_manager = self.data.get("is_manager")
            QuerySet(TeamMember).filter(id=member_id).update(is_manager=is_manager)
            return True

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='member_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('Member id')), ]


class TeamSerializer(ApiMixin, serializers.Serializer):
    team_name = serializers.CharField(max_length=100)

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['team_id', 'team_name', 'role', 'role'],
            properties={
                'team_id': openapi.Schema(type=openapi.TYPE_STRING, title=_('team id'), description=_('teeam id')),
                'team_name': openapi.Schema(type=openapi.TYPE_STRING, title=_('team name'), description=_('team name')),
                'role': openapi.Schema(type=openapi.TYPE_STRING, title=_('Role'), description=_('Role')),
            }
        )

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['team_name'],
            properties={
                'team_name': openapi.Schema(type=openapi.TYPE_STRING, title=_('Team name'),
                                            description=_('Team name'))
            }
        )

    def add_team(self, user_id, team_name, with_valid=True):
        """
        添加一个团队
        :param with_valid: 是否校驗參數
        :param team_name: 添加团队名称
        :return: 成员列表
        """
        if with_valid:
            self.is_valid(raise_exception=True)
        user = QuerySet(User).get(id=user_id)
        if user.role != "ADMIN":
            raise AppApiException(500, _('The current user not permission'))
        team = QuerySet(Team).filter(name=self.data.get('name')).first()
        if team:
            raise AppApiException(500, _('The current team already exist in the team, do not add them again.'))
        team = Team(name=self.data.get("team_name"))
        team.save()
        TeamMember.objects.create(
            team=team,
            user=user,
            is_manager=False
        )
        return self.get_team_list(user_id, with_valid=False)

    def get_team_list(self, user_id, with_valid=True):
        """
        获取 团队列表
        :return: 团队列表
        """
        if with_valid:
            self.is_valid(raise_exception=True)
        user = QuerySet(User).get(id=user_id)
        if user.role == "ADMIN":
            query_set = QuerySet(Team).all().order_by('name')
            member_list = list(map(lambda t: {"team_id": str(t.id), 'team_name': t.name, "role": "admin"},
                                   query_set))
        else:
            query_set = Team.objects.filter(teammember__user=user).order_by('name')
            member_list = list(map(lambda t: {"team_id": str(t.id), 'team_name': t.name,
                                              "role": "manager" if TeamMember.objects.get(user_id=user_id,
                                                                                          team_id=str(
                                                                                              t.id)).is_manager else "member"},
                                   query_set))
        return sorted(member_list, key=lambda x: x['role'] != 'manager')

    class Operate(ApiMixin, serializers.Serializer):

        team_id = serializers.CharField(required=True, error_messages=ErrMessage.char(_('team id')))
        team_name = serializers.CharField(required=False, error_messages=ErrMessage.char(_('team name')))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)

        def edit(self, user_id, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            team_id = self.data.get("team_id")
            user = User.objects.get(id=user_id)
            team_member = TeamMember.objects.get(user_id=user_id, team_id=team_id)
            if user.role != "ADMIN" and not team_member.is_manager:
                raise AppApiException(403, _('Permission denied. Only admin or team manager can delete team.'))
            Team.objects.filter(id=team_id).update(name=self.data.get("team_name"))
            return True

        def delete(self, user_id, with_valid=True):
            """
            删除团队及团队成员成员
            :return:
            """
            if with_valid:
                self.is_valid(raise_exception=True)
            team_id = self.data.get("team_id")
            user = User.objects.get(id=user_id)
            team_member = TeamMember.objects.get(user_id=user_id, team_id=team_id)
            if user.role != "ADMIN" and not team_member.is_manager:
                raise AppApiException(403, _('Permission denied. Only admin or team manager can delete team.'))
            with transaction.atomic():
                TeamMember.objects.filter(team_id=team_id).delete()
                Team.objects.filter(id=team_id).delete()
            return True

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='team_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('Team id')), ]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['team_name'],
                properties={
                    'team_name': openapi.Schema(type=openapi.TYPE_STRING, title=_('Team name'),
                                                description=_('Team name'))

                }
            )


class TeamMemberInstanceSerializer(ApiMixin, serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    role = serializers.CharField(source='user.role')
    is_manager = serializers.BooleanField()
    team_member_type = serializers.SerializerMethodField()

    class Meta:
        model = TeamMember
        fields = [
            'id', 'team_id', 'user_id',
            'team_member_type', 'username',
            'email', 'role', 'is_manager'
        ]

    def get_team_member_type(self, obj):
        role = obj.user.role
        is_manager = obj.is_manager
        if role == "ADMIN":
            return "admin"
        elif is_manager:
            return "manager"
        else:
            return "member"
