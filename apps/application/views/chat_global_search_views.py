from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from datetime import datetime

from application.models.application import ChatRecord
from common.response import result
from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import RoleConstants


class GlobalChatSearchView(APIView):
    """
    全局对话日志搜索视图
    """
    authentication_classes = [TokenAuth]
    
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    def get(self, request):
        """
        搜索对话记录
        """
        try:
            # 获取当前用户
            user = request.user
            
            # 获取查询参数
            query = request.GET.get('query', '')
            application_id = request.GET.get('application_id', '')
            current_page = int(request.GET.get('current_page', 1))
            page_size = int(request.GET.get('page_size', 20))
            start_date = request.GET.get('start_date', '')
            end_date = request.GET.get('end_date', '')
            
            # 构建查询条件
            queryset = ChatRecord.objects.select_related('chat__application__user').all()
            
            # 根据用户权限过滤 - 简化权限检查
            try:
                if hasattr(user, 'role') and user.role != 'ADMIN':
                    # 普通用户只能查看自己创建的对话记录
                    queryset = queryset.filter(chat__application__user_id=user.id)
            except:
                # 如果无法确定用户角色，默认只显示用户自己的记录
                queryset = queryset.filter(chat__application__user_id=user.id)
            
            # 应用过滤
            if application_id:
                queryset = queryset.filter(chat__application_id=application_id)
            
            # 文本搜索
            if query:
                queryset = queryset.filter(
                    Q(problem_text__icontains=query) | 
                    Q(answer_text__icontains=query)
                )
            
            # 日期范围过滤
            if start_date:
                queryset = queryset.filter(create_time__gte=start_date)
            if end_date:
                queryset = queryset.filter(create_time__lte=end_date + ' 23:59:59')
            
            # 排序
            queryset = queryset.order_by('-create_time')
            
            # 分页
            total = queryset.count()
            start = (current_page - 1) * page_size
            end = start + page_size
            records = queryset[start:end]
            
            # 构建返回数据
            result_records = []
            for record in records:
                try:
                    application_name = record.chat.application.name if record.chat.application else '未知应用'
                    user_name = record.chat.application.user.username if (record.chat.application and record.chat.application.user) else '未知用户'
                    
                    result_records.append({
                        'id': str(record.id),
                        'chat_id': str(record.chat.id),
                        'application_id': str(record.chat.application_id),
                        'application_name': application_name,
                        'problem_text': record.problem_text or '',
                        'answer_text': record.answer_text or '',
                        'create_time': record.create_time.isoformat() if record.create_time else None,
                        'message_tokens': record.message_tokens or 0,
                        'answer_tokens': record.answer_tokens or 0,
                        'vote_status': record.vote_status or '',
                        'user_name': user_name
                    })
                except Exception as e:
                    # 跳过有问题的记录，继续处理其他记录
                    print(f"处理记录时出错: {e}")
                    continue
            
            return result.success({
                'records': result_records,
                'total': total,
                'current_page': current_page,
                'page_size': page_size
            })
            
        except Exception as e:
            print(f"搜索失败: {str(e)}")
            return result.error(f"搜索失败: {str(e)}", response_status=status.HTTP_500_INTERNAL_SERVER_ERROR) 