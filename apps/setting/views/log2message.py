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
        logs = Log.objects.filter(
            menu='Knowledge Base',
            operate__in=['将知识库添加到机构知识库', '更新数据集分享权限'],
        ).order_by('-create_time')[:50]

        # Process logs and convert them to messages
        messages = [{
            "msg": log.to_message(),
            "log_id": str(log.id),
            "log_read": log.log_read,
            "create_time": log.create_time.strftime('%Y-%m-%d %H:%M:%S')
        } for log in logs if log.details['body'].get('user_id', None) in {request.user.id, None}]
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
