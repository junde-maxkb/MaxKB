#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试删除功能是否正确实现软删除
"""

import os
import sys
import django

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartdoc.conf')
django.setup()

from dataset.models.data_set import DataSet
from dataset.serializers.dataset_serializers import DataSetSerializers
from django.utils import timezone

def test_delete_functionality():
    """测试删除功能"""
    print("开始测试删除功能...")
    
    # 1. 检查当前知识库状态
    total_datasets = DataSet.objects.count()
    active_datasets = DataSet.objects.filter(is_deleted=False).count()
    deleted_datasets = DataSet.objects.filter(is_deleted=True).count()
    
    print(f"总知识库数量: {total_datasets}")
    print(f"正常知识库数量: {active_datasets}")
    print(f"已删除知识库数量: {deleted_datasets}")
    
    # 2. 查找一个可以测试的知识库
    test_dataset = DataSet.objects.filter(is_deleted=False).first()
    if not test_dataset:
        print("没有可用的知识库进行测试")
        return
    
    print(f"\n测试知识库: {test_dataset.name} (ID: {test_dataset.id})")
    print(f"当前删除状态: is_deleted={test_dataset.is_deleted}, delete_time={test_dataset.delete_time}")
    
    # 3. 测试软删除功能
    print("\n执行软删除...")
    try:
        # 创建操作对象
        operate = DataSetSerializers.Operate(data={'id': str(test_dataset.id)})
        operate.is_valid()
        
        # 执行删除
        result = operate.delete()
        print(f"删除结果: {result}")
        
        # 重新查询知识库
        test_dataset.refresh_from_db()
        print(f"删除后状态: is_deleted={test_dataset.is_deleted}, delete_time={test_dataset.delete_time}")
        
        if test_dataset.is_deleted:
            print("✅ 软删除成功！知识库已被标记为已删除")
        else:
            print("❌ 软删除失败！知识库未被标记为已删除")
            
    except Exception as e:
        print(f"❌ 删除操作失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. 测试恢复功能
    print("\n执行恢复操作...")
    try:
        # 执行恢复
        result = operate.restore()
        print(f"恢复结果: {result}")
        
        # 重新查询知识库
        test_dataset.refresh_from_db()
        print(f"恢复后状态: is_deleted={test_dataset.is_deleted}, delete_time={test_dataset.delete_time}")
        
        if not test_dataset.is_deleted:
            print("✅ 恢复成功！知识库已被恢复")
        else:
            print("❌ 恢复失败！知识库仍被标记为已删除")
            
    except Exception as e:
        print(f"❌ 恢复操作失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 5. 验证最终状态
    print("\n验证最终状态...")
    final_total = DataSet.objects.count()
    final_active = DataSet.objects.filter(is_deleted=False).count()
    final_deleted = DataSet.objects.filter(is_deleted=True).count()
    
    print(f"最终总知识库数量: {final_total}")
    print(f"最终正常知识库数量: {final_active}")
    print(f"最终已删除知识库数量: {final_deleted}")
    
    if final_total == total_datasets and final_active == active_datasets and final_deleted == deleted_datasets:
        print("✅ 测试完成！知识库数量保持一致，软删除功能正常")
    else:
        print("❌ 测试异常！知识库数量发生变化")

if __name__ == "__main__":
    test_delete_functionality() 