#!/usr/bin/env python
"""
测试回收站恢复功能
"""
import os
import sys
import django

# 添加项目路径
sys.path.insert(0, '/d:/Project/MaxKB-jd/MaxKB')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartdoc.settings.common')

django.setup()

from dataset.models.data_set import DataSet
from dataset.serializers.dataset_serializers import DataSetSerializers
from django.db.models import QuerySet

def test_restore_function():
    """测试恢复功能"""
    print("开始测试回收站恢复功能...")
    
    # 1. 查找已删除的知识库
    deleted_datasets = QuerySet(DataSet).filter(is_deleted=True)
    print(f"找到 {len(deleted_datasets)} 个已删除的知识库")
    
    if len(deleted_datasets) == 0:
        print("没有找到已删除的知识库，请先删除一个知识库进行测试")
        return
    
    # 取第一个进行测试
    test_dataset = deleted_datasets.first()
    print(f"测试知识库: {test_dataset.name} (ID: {test_dataset.id})")
    print(f"删除状态: is_deleted={test_dataset.is_deleted}, delete_time={test_dataset.delete_time}")
    
    # 2. 测试恢复操作
    try:
        operate = DataSetSerializers.Operate(data={'id': str(test_dataset.id)})
        result = operate.restore()
        print(f"恢复操作结果: {result}")
        
        # 3. 验证恢复后的状态
        test_dataset.refresh_from_db()
        print(f"恢复后状态: is_deleted={test_dataset.is_deleted}, delete_time={test_dataset.delete_time}")
        
        if not test_dataset.is_deleted and test_dataset.delete_time is None:
            print("✅ 恢复功能测试成功！")
        else:
            print("❌ 恢复功能测试失败！")
            
    except Exception as e:
        print(f"❌ 恢复操作失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_restore_function() 