import uuid
from django.db import models


class DatabaseType(models.TextChoices):
    MYSQL = ('mysql', 'MySQL')
    POSTGRESQL = ('postgresql', 'PostgreSQL')
    ORACLE = ('oracle', 'Oracle')
    SQLSERVER = ('sqlserver', 'SQL Server')
    MONGODB = ('mongodb', 'MongoDB')

    @classmethod
    def get_value(cls, member):
        return cls[member].value[0]

    @classmethod
    def get_label(cls, member):
        return cls[member].value[1]

    @classmethod
    def choices(cls):
        return [(item.value[0], item.value[1]) for item in cls]


class DataSourceConfig(models.Model):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    db_type = models.CharField(verbose_name='数据库类型', max_length=20,
                               choices=DatabaseType.choices, default=DatabaseType.MYSQL.value)
    name = models.CharField(max_length=255, verbose_name="数据源名称", unique=True)
    description = models.TextField(max_length=1024, verbose_name="数据源描述")
    host = models.CharField(max_length=255, verbose_name="主机地址")
    port = models.IntegerField(verbose_name="端口")
    database_name = models.CharField(max_length=255, verbose_name="数据库名称")
    username = models.CharField(max_length=255, verbose_name="用户名")
    password = models.CharField(max_length=255, verbose_name="密码")
    ssh_enabled = models.BooleanField(default=False, verbose_name="启用SSH设置")
    ssh_config = models.JSONField(verbose_name="ssh配置", default=dict, blank=True, null=True)
    advanced = models.JSONField(verbose_name="高级配置", default=dict, blank=True, null=True)
    extra_params = models.JSONField(verbose_name="扩展参数", default=dict, blank=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "data_source_config"
        verbose_name = "数据库连接配置"