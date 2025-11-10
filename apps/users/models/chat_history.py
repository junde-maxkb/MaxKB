# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： chat_history.py
    @date：2024/12/19
    @desc: 历史聊天记录模型
"""
import uuid

from django.db import models

from common.mixins.app_model_mixin import AppModelMixin
from users.models.user import User

__all__ = ["ChatHistory", "ChatMessage"]


class ChatHistory(AppModelMixin):
    """
    历史聊天记录表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户ID", related_name="chat_histories")
    application_name = models.CharField(max_length=128, verbose_name="应用名称", default="")
    title = models.CharField(max_length=256, verbose_name="聊天标题", default="", blank=True)
    message_count = models.IntegerField(default=0, verbose_name="消息数量")
    
    class Meta:
        db_table = "chat_history"
        verbose_name = "历史聊天记录"
        verbose_name_plural = verbose_name
        ordering = ['-create_time']  # 按创建时间倒序排列


class ChatMessage(AppModelMixin):
    """
    聊天消息表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    chat_history = models.ForeignKey(ChatHistory, on_delete=models.CASCADE, verbose_name="聊天历史ID", related_name="messages")
    role = models.CharField(max_length=20, verbose_name="角色", default="user")  # 'user' | 'assistant' | 'system'
    content = models.TextField(verbose_name="消息内容", default="")
    message_index = models.IntegerField(default=0, verbose_name="消息序号")  # 用于排序
    
    class Meta:
        db_table = "chat_message"
        verbose_name = "聊天消息"
        verbose_name_plural = verbose_name
        ordering = ['message_index', 'create_time']  # 按序号和时间排序

