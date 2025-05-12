# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： authentication.py
    @date：2023/9/13 15:00
    @desc: 鉴权
"""
from typing import List

from common.constants.permission_constants import ViewPermission, CompareConstants, RoleConstants, PermissionConstants, \
    Permission
from common.exception.app_exception import AppUnauthorizedFailed
from django.utils.translation import gettext_lazy as _

def exist_permissions_by_permission_constants(user_permission: List[PermissionConstants],
                                              permission_list: List[PermissionConstants]):
    """
    用户是否拥有 permission_list的权限
    :param user_permission:  用户权限
    :param permission_list:  需要的权限
    :return: 是否拥有
    """
    return any(list(map(lambda up: permission_list.__contains__(up), user_permission)))


def exist_role_by_role_constants(user_role: List[RoleConstants],
                                 role_list: List[RoleConstants]):
    """
    用户是否拥有这个角色
    :param user_role: 用户角色
    :param role_list: 需要拥有的角色
    :return:  是否拥有
    """
    return any(list(map(lambda up: role_list.__contains__(up), user_role)))


def exist_permissions_by_view_permission(user_role: List[RoleConstants],
                                         user_permission: List[PermissionConstants | object],
                                         permission: ViewPermission, request, **kwargs):
    """
    用户是否存在这些权限
    :param request:
    :param user_role:        用户角色
    :param user_permission:  用户权限
    :param permission:       所属权限
    :return:                 是否存在 True False
    """
    role_ok = any(list(map(lambda ur: permission.roleList.__contains__(ur), user_role)))
    permission_list = [user_p(request, kwargs) if callable(user_p) else user_p for user_p in
                       permission.permissionList
                       ]
    permission_ok = any(list(map(lambda up: permission_list.__contains__(up),
                                 user_permission)))
    return role_ok | permission_ok if permission.compare == CompareConstants.OR else role_ok & permission_ok


def exist_permissions(user_role: List[RoleConstants], user_permission: List[PermissionConstants], permission, request,
                      **kwargs):
    if isinstance(permission, ViewPermission):
        return exist_permissions_by_view_permission(user_role, user_permission, permission, request, **kwargs)
    if isinstance(permission, RoleConstants):
        return exist_role_by_role_constants(user_role, [permission])
    if isinstance(permission, PermissionConstants):
        return exist_permissions_by_permission_constants(user_permission, [permission])
    if isinstance(permission, Permission):
        return user_permission.__contains__(permission)
    return False


def exist(user_role: List[RoleConstants], user_permission: List[PermissionConstants], permission, request, **kwargs):
    if callable(permission):
        p = permission(request, kwargs)
        return exist_permissions(user_role, user_permission, p, request)
    return exist_permissions(user_role, user_permission, permission, request, **kwargs)


def get_user_dataset_permission(user, dataset_id):
    """
    获取用户对特定知识库的权限
    :param user: 用户对象
    :param dataset_id: 知识库ID
    :return: 权限级别（'MANAGE', 'WRITE', 'READ'）或 None
    """
    from setting.models.team_management import TeamMember
    from dataset.models import DatasetShare, DataSet
    from django.db.models import Q

    print(f"正在获取用户 {user.id} 对知识库 {dataset_id} 的权限")

    # 检查个人权限
    try:
        if DataSet.objects.get(id=dataset_id).user_id == user.id:
            return 'MANAGE'
        dataset_member = DatasetShare.objects.get(shared_with_type='USER', dataset_id=dataset_id, shared_with_id=user.id)
        print(f"用户 {user.id} 对知识库 {dataset_id} 有个人权限: {dataset_member.permission}")
        return dataset_member.permission
        
    except DatasetShare.DoesNotExist:
        print(f"用户 {user.id} 对知识库 {dataset_id} 没有个人权限")
        pass

    # 检查团队权限
    user_teams = TeamMember.objects.filter(Q(user_id=user.id) | Q(team_id=user.id)).values_list('team_id', flat=True)
    print(f"用户 {user.id} 所在的团队: {list(user_teams)}")
    team_permissions = DatasetShare.objects.filter(shared_with_type='TEAM', dataset_id=dataset_id, shared_with_id__in=user_teams)
    
    if team_permissions.exists():
        # 返回最高级别的团队权限
        permissions = team_permissions.values_list('permission', flat=True)
        print(f"用户 {user.id} 通过团队获得的权限: {list(permissions)}")
        if 'MANAGE' in permissions:
            print(f"用户 {user.id} 对知识库 {dataset_id} 有管理权限")
            return 'MANAGE'
        elif 'WRITE' in permissions:
            print(f"用户 {user.id} 对知识库 {dataset_id} 有写入权限")
            return 'WRITE'
        elif 'READ' in permissions:
            print(f"用户 {user.id} 对知识库 {dataset_id} 有读取权限")
            return 'READ'

    print(f"用户 {user.id} 对知识库 {dataset_id} 没有任何权限")
    return None

def has_permissions(*permission, compare=CompareConstants.OR, dataset_permission=None):
    """
    权限 role or permission
    :param compare:    比较符号
    :param permission: 如果是角色 role:roleId
    :param dataset_permission: 知识库权限
    :return: 权限装饰器函数,用于判断用户是否有权限访问当前接口
    """

    def inner(func):
        def run(view, request, **kwargs):
            # print(f"正在检查用户 {request.user.id} 的权限")
            exit_list = list(
                map(lambda p: exist(request.auth.role_list, request.auth.permission_list, p, request, **kwargs),
                    permission))
            # print(f"权限检查结果: {exit_list}")
            
            # 检查知识库权限
            dataset_permission_passed = True  # 默认通过知识库权限检查
            if dataset_permission:
                dataset_id = kwargs.get('dataset_id')
                if dataset_id:
                    # print(f"正在检查用户 {request.user.id} 对知识库 {dataset_id} 的权限")
                    user_dataset_permission = get_user_dataset_permission(request.user, dataset_id)
                    print(f"用户 {request.user.id} 对知识库 {dataset_id} 的权限: {user_dataset_permission}")
                    if user_dataset_permission:
                        if dataset_permission == 'MANAGE' and user_dataset_permission != 'MANAGE':
                            # print(f"用户 {request.user.id} 没有管理知识库 {dataset_id} 的权限")
                            dataset_permission_passed = False
                            raise AppUnauthorizedFailed(403, _('无权管理此知识库'))
                        elif dataset_permission == 'WRITE' and user_dataset_permission not in ['MANAGE', 'WRITE']:
                            # print(f"用户 {request.user.id} 没有写入知识库 {dataset_id} 的权限")
                            dataset_permission_passed = False
                            raise AppUnauthorizedFailed(403, _('无权写入此知识库'))
                        elif dataset_permission == 'READ' and user_dataset_permission not in ['MANAGE', 'WRITE', 'READ']:
                            # print(f"用户 {request.user.id} 没有读取知识库 {dataset_id} 的权限")
                            dataset_permission_passed = False
                            raise AppUnauthorizedFailed(403, _('无权读取此知识库'))
                    else:
                        # print(f"用户 {request.user.id} 没有访问知识库 {dataset_id} 的权限")
                        dataset_permission_passed = False
                        raise AppUnauthorizedFailed(403, _('无权访问此知识库'))

            # 判断是否有权限
            # if any(exit_list) if compare == CompareConstants.OR else all(exit_list):
            #     print(f"用户 {request.user.id} 通过权限检查")
            #     return func(view, request, **kwargs)
            # print(f"用户 {request.user.id} 没有访问权限")
            # raise AppUnauthorizedFailed(403, _('No permission to access'))
            general_permission_passed = any(exit_list) if compare == CompareConstants.OR else all(exit_list)
            print(dataset_permission_passed)
            if general_permission_passed or dataset_permission_passed:
                # print(f"用户 {request.user.id} 通过权限检查")
                return func(view, request, **kwargs)
            
            # print(f"用户 {request.user.id} 没有访问权限")
            raise AppUnauthorizedFailed(403, _('无访问权限'))

        return run

    return inner
