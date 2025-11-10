from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import PermissionConstants
from common.log.log import log
from common.response import result
from dataset.models import DataSet
from setting.models import Team
from setting.serializers.team_serializers import TeamMemberSerializer, get_response_body_api, \
    UpdateTeamMemberPermissionSerializer
from django.utils.translation import gettext_lazy as _
from setting.models.log_management import Log
from setting.views.common import get_member_operation_object, get_member_operation_object_batch


class Log2Message(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('Convert Logs to Messages'),
                         operation_id=_('Convert Logs to Messages'),
                         tags=[_('Log')])
    @has_permissions(PermissionConstants.USER_READ)
    def get(self, request: Request):

        user = request.user
        # 获取当前用户所处团队
        teams = {i.id: i.name for i in Team.objects.filter(teammember__user=user).all()}

        logs = Log.objects.filter(
            menu='Knowledge Base',
            operate__in=['将知识库添加到机构知识库', '更新数据集分享权限'],
        ).order_by('-create_time')[:50]

        # Process logs and convert them to messages
        messages = []
        for log_item in logs:
            share_user_name = log_item.user.get('username', None)
            # '/api/dataset/0adba462-b3c2-11f0-9ffe-1df6b9a97501/members/put_permissions'
            dataset_id = log_item.details['path'].split('/')[3] if len(log_item.details['path'].split('/')) > 3 else ''
            dataset_name = DataSet.objects.filter(id=dataset_id).first().name if dataset_id else '未知知识库'
            if log_item.operate == "将知识库添加到机构知识库":
                messages.append({
                    "msg": "{} 将知识库 '{}' 添加到机构知识库".format(
                        share_user_name,
                        dataset_name),

                    "log_id": str(log_item.id),
                    "log_read": log_item.log_read,
                    "create_time": log_item.create_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            elif log_item.details['body'].get('share_with_type', None) == "TEAM":
                team_id = log_item.details['body'].get('user_id', None)
                if team_id not in teams: continue
                messages.append({
                    "msg": "{} 更新了知识库 '{}' 在团队 '{}' 的分享权限".format(
                        share_user_name,
                        dataset_name,
                        teams.get(team_id, '未知团队')
                    ),
                    "log_id": str(log_item.id),
                    "log_read": log_item.log_read,
                    "create_time": log_item.create_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            elif log_item.details['body'].get('share_with_type', None) == "USER":
                if str(log_item.details['body'].get('user_id', None)) != str(user.id): continue
                messages.append({
                    "msg": "{} 更新了知识库 '{}' 分享给您的权限".format(
                        share_user_name,
                        dataset_name
                    ),
                    "log_id": str(log_item.id),
                    "log_read": log_item.log_read,
                    "create_time": log_item.create_time.strftime('%Y-%m-%d %H:%M:%S')
                })
        return result.success(data=messages)

    @action(methods=['PUT'], detail=False)
    @swagger_auto_schema(operation_summary=_('Mark Log as Read'),
                         operation_id=_('Mark Log as Read'),
                         tags=[_('Log')])
    @has_permissions(PermissionConstants.USER_READ)
    def put(self, request: Request):
        log_id = request.data.get('log_id')
        try:
            log_entry = Log.objects.get(id=log_id)
            log_entry.log_read = True
            log_entry.save()
            return result.success(message="Log marked as read.", data={})
        except Log.DoesNotExist:
            return result.fail(message="Log not found.", status=404)
