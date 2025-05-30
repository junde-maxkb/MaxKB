from rest_framework import serializers


from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin

from django.utils.translation import gettext_lazy as _

from setting.models.data_source import DataSourceConfig

FIELD = serializers.IntegerField(min_value=1, max_value=65535)



class DBConfigerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    db_type = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=255)
    host = serializers.CharField(max_length=255)
    port = serializers.IntegerField()
    database_name = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
    ssh_enabled = serializers.BooleanField()
    advanced = serializers.JSONField(required=False)
    ssh_config = serializers.JSONField(required=False)
    extra_params = serializers.JSONField(required=False)

    class Meta:
        model = DataSourceConfig
        fields = '__all__'


    def add_data_source(self,with_valid=True):
        """
        添加一个sql数据源
        :param with_valid:
        :param team_name:
        :return:
        """
        if with_valid:
            self.is_valid(raise_exception=True)
        user = DataSourceConfig.objects.filter(name=self.data['name']).first()
        if user:
            raise AppApiException(500, _('The current source already exist'))
        DataSourceConfig.objects.create(
           **self.data
        )
        return True


    class Operate(ApiMixin, serializers.Serializer):

        id = serializers.UUIDField(required=True)

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            return True

        def edit(self, data, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            if not self.is_valid():
                raise AppApiException(403, _('Permission denied.'))

            data_source = DataSourceConfig.objects.get(id = self.data.get('id'))
            if not data_source:
                raise AppApiException(403, _('Permission denied.'))
            DataSourceConfig.objects.filter(id=self.data.get('id')).update(**data)
            return True

        def delete(self, id, with_valid=True):
            """

            :return:
            """
            if with_valid:
                self.is_valid(raise_exception=True)
            DataSourceConfig.objects.filter(id=id).delete()
            return True


class DBConnectionSerializer(serializers.Serializer):
    db_type = serializers.ChoiceField(choices=['mysql', 'postgresql'])
    host = serializers.CharField()
    port = serializers.IntegerField(min_value=1, max_value=65535)
    username = serializers.CharField()
    password = serializers.CharField()
    database_name = serializers.CharField()
    extra_params = serializers.JSONField(required=False)
