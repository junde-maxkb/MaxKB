#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回收站功能修复测试脚本
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

def test_recycle_bin_data_structure():
    """测试回收站数据结构"""
    print("开始测试回收站数据结构...")
    
    # 1. 检查是否有已删除的知识库
    deleted_datasets = DataSet.objects.filter(is_deleted=True)
    print(f"已删除的知识库数量: {deleted_datasets.count()}")
    
    if not deleted_datasets.exists():
        print("没有已删除的知识库，创建一个测试数据...")
        # 创建一个测试知识库并软删除
        test_dataset = DataSet.objects.filter(is_deleted=False).first()
        if test_dataset:
            test_dataset.is_deleted = True
            test_dataset.delete_time = timezone.now()
            test_dataset.save()
            print(f"已创建测试数据: {test_dataset.name}")
        else:
            print("没有可用的知识库进行测试")
            return
    
    # 2. 测试RecycleBinQuery的page方法
    try:
        # 获取第一个用户的ID
        user_id = DataSet.objects.first().user_id
        print(f"使用用户ID: {user_id}")
        
        # 创建查询对象
        query_data = {
            'user_id': str(user_id),
            'name': None,
            'desc': None
        }
        
        recycle_bin_query = DataSetSerializers.RecycleBinQuery(data=query_data)
        recycle_bin_query.is_valid()
        
        # 测试page方法
        result = recycle_bin_query.page(1, 10)
        print(f"Page方法返回结果类型: {type(result)}")
        print(f"返回结果键: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict) and 'list' in result:
            print(f"✅ 数据结构正确，包含'list'键")
            print(f"列表长度: {len(result['list'])}")
            print(f"总数: {result.get('total', 0)}")
            
            if result['list']:
                first_item = result['list'][0]
                print(f"第一个项目键: {list(first_item.keys())}")
                print(f"第一个项目示例: {first_item}")
        else:
            print(f"❌ 数据结构不正确: {result}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n回收站数据结构测试完成!")

if __name__ == "__main__":
    test_recycle_bin_data_structure() 