#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试删除操作
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

def debug_delete_operation():
    """调试删除操作"""
    print("开始调试删除操作...")
    
    # 1. 检查当前知识库状态
    total_datasets = DataSet.objects.count()
    active_datasets = DataSet.objects.filter(is_deleted=False).count()
    deleted_datasets = DataSet.objects.filter(is_deleted=True).count()
    
    print(f"总知识库数量: {total_datasets}")
    print(f"正常知识库数量: {active_datasets}")
    print(f"已删除知识库数量: {deleted_datasets}")
    
    # 2. 显示所有知识库的详细信息
    print("\n所有知识库详细信息:")
    for dataset in DataSet.objects.all():
        print(f"  ID: {dataset.id}")
        print(f"  名称: {dataset.name}")
        print(f"  用户ID: {dataset.user_id}")
        print(f"  是否删除: {dataset.is_deleted}")
        print(f"  删除时间: {dataset.delete_time}")
        print(f"  创建时间: {dataset.create_time}")
        print("  ---")
    
    # 3. 查找一个可以测试的知识库
    test_dataset = DataSet.objects.filter(is_deleted=False).first()
    if not test_dataset:
        print("没有可用的知识库进行测试")
        return
    
    print(f"\n测试知识库: {test_dataset.name} (ID: {test_dataset.id})")
    print(f"当前删除状态: is_deleted={test_dataset.is_deleted}, delete_time={test_dataset.delete_time}")
    
    # 4. 测试软删除功能
    print("\n执行软删除...")
    try:
        # 创建操作对象
        operate = DataSetSerializers.Operate(data={'id': str(test_dataset.id)})
        print(f"操作对象创建成功: {operate}")
        
        # 验证数据
        operate.is_valid()
        print(f"数据验证通过: {operate.data}")
        
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
    
    # 5. 检查回收站查询
    print("\n测试回收站查询...")
    try:
        # 获取用户ID
        user_id = test_dataset.user_id
        print(f"使用用户ID: {user_id}")
        
        # 创建回收站查询对象
        recycle_bin_query = DataSetSerializers.RecycleBinQuery(data={
            'user_id': str(user_id),
            'name': None,
            'desc': None
        })
        recycle_bin_query.is_valid()
        
        # 测试page方法
        result = recycle_bin_query.page(1, 10)
        print(f"回收站查询结果: {result}")
        
        if isinstance(result, dict) and 'list' in result:
            print(f"回收站列表长度: {len(result['list'])}")
            if result['list']:
                print("回收站中的知识库:")
                for item in result['list']:
                    print(f"  - {item['name']} (ID: {item['id']})")
            else:
                print("回收站为空")
        else:
            print(f"❌ 回收站查询返回格式错误: {result}")
            
    except Exception as e:
        print(f"❌ 回收站查询失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_delete_operation() 