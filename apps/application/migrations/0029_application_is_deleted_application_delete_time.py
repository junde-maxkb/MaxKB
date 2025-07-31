# Generated manually for application soft delete feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0028_organizationapplication'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='是否已删除'),
        ),
        migrations.AddField(
            model_name='application',
            name='delete_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='删除时间'),
        ),
    ]