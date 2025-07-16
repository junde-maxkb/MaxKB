#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的回收站API测试
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

def test_recycle_bin_api():
    """测试回收站API"""
    print("测试回收站API...")
    
    # 检查是否有已删除的知识库
    deleted_count = DataSet.objects.filter(is_deleted=True).count()
    print(f"已删除的知识库数量: {deleted_count}")
    
    if deleted_count == 0:
        print("没有已删除的知识库，跳过测试")
        return
    
    # 获取第一个已删除的知识库的用户ID
    deleted_dataset = DataSet.objects.filter(is_deleted=True).first()
    user_id = deleted_dataset.user_id
    print(f"使用用户ID: {user_id}")
    
    # 创建查询对象
    query_data = {
        'user_id': str(user_id),
        'name': None,
        'desc': None
    }
    
    try:
        recycle_bin_query = DataSetSerializers.RecycleBinQuery(data=query_data)
        recycle_bin_query.is_valid()
        
        # 测试page方法
        result = recycle_bin_query.page(1, 10)
        print(f"✅ Page方法成功执行")
        print(f"返回数据结构: {type(result)}")
        
        if isinstance(result, dict):
            print(f"返回键: {list(result.keys())}")
            if 'list' in result:
                print(f"✅ 包含'list'键")
                print(f"列表长度: {len(result['list'])}")
                print(f"总数: {result.get('total', 0)}")
                
                if result['list']:
                    first_item = result['list'][0]
                    print(f"第一个项目键: {list(first_item.keys())}")
                    print(f"示例数据: {first_item}")
            else:
                print(f"❌ 缺少'list'键")
        else:
            print(f"❌ 返回的不是字典: {result}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_recycle_bin_api() 