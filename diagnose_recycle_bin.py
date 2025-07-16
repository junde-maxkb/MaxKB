#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回收站功能全面诊断脚本
"""

import os
import sys
import django
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartdoc.conf')
django.setup()

from dataset.models.data_set import DataSet
from dataset.serializers.dataset_serializers import DataSetSerializers
from django.utils import timezone

def diagnose_recycle_bin():
    """全面诊断回收站功能"""
    print("=" * 60)
    print("回收站功能全面诊断")
    print("=" * 60)
    
    # 1. 检查数据库中的软删除数据
    print("\n1. 检查数据库中的软删除数据")
    print("-" * 40)
    
    all_datasets = DataSet.objects.all()
    deleted_datasets = DataSet.objects.filter(is_deleted=True)
    active_datasets = DataSet.objects.filter(is_deleted=False)
    
    print(f"总知识库数量: {all_datasets.count()}")
    print(f"正常知识库数量: {active_datasets.count()}")
    print(f"已删除知识库数量: {deleted_datasets.count()}")
    
    if deleted_datasets.exists():
        print("\n已删除的知识库详情:")
        for i, dataset in enumerate(deleted_datasets, 1):
            print(f"  {i}. ID: {dataset.id}")
            print(f"     名称: {dataset.name}")
            print(f"     用户ID: {dataset.user_id}")
            print(f"     删除状态: {dataset.is_deleted}")
            print(f"     删除时间: {dataset.delete_time}")
            print(f"     创建时间: {dataset.create_time}")
            print()
    else:
        print("❌ 数据库中没有 is_deleted=True 的数据！")
        return
    
    # 2. 测试回收站序列化器的各个方法
    print("\n2. 测试回收站序列化器")
    print("-" * 40)
    
    try:
        # 创建查询对象（不传user_id，因为我们已经去掉了这个过滤条件）
        query_data = {
            'user_id': '',  # 空值
            'name': None,
            'desc': None
        }
        
        recycle_bin_query = DataSetSerializers.RecycleBinQuery(data=query_data)
        print(f"序列化器创建成功: {recycle_bin_query}")
        
        # 验证数据
        is_valid = recycle_bin_query.is_valid()
        print(f"数据验证结果: {is_valid}")
        if not is_valid:
            print(f"验证错误: {recycle_bin_query.errors}")
        
        # 测试get_query_set方法
        query_set = recycle_bin_query.get_query_set()
        query_count = query_set.count()
        print(f"get_query_set查询到的数量: {query_count}")
        
        if query_count > 0:
            print("get_query_set查询到的数据:")
            for i, item in enumerate(query_set[:3], 1):  # 只显示前3个
                print(f"  {i}. {item.name} (ID: {item.id}, User: {item.user_id})")
        
        # 测试page方法
        page_result = recycle_bin_query.page(1, 10)
        print(f"\npage方法返回类型: {type(page_result)}")
        print(f"page方法返回键: {list(page_result.keys()) if isinstance(page_result, dict) else 'Not a dict'}")
        
        if isinstance(page_result, dict):
            list_data = page_result.get('list', [])
            total = page_result.get('total', 0)
            print(f"返回列表长度: {len(list_data)}")
            print(f"总数: {total}")
            
            if list_data:
                print("返回的第一个项目:")
                first_item = list_data[0]
                print(json.dumps(first_item, indent=2, ensure_ascii=False))
            else:
                print("❌ 返回的列表为空!")
        else:
            print(f"❌ page方法返回格式错误: {page_result}")
            
    except Exception as e:
        print(f"❌ 序列化器测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 3. 模拟API调用
    print("\n3. 模拟API调用")
    print("-" * 40)
    
    try:
        from dataset.views.dataset import Dataset
        from django.http import HttpRequest
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # 创建模拟请求
        request = HttpRequest()
        request.method = 'GET'
        request.META = {}
        
        # 模拟用户
        first_user = User.objects.first()
        if first_user:
            request.user = first_user
            print(f"使用用户: {first_user.username} (ID: {first_user.id})")
            
            # 创建视图实例
            view = Dataset.RecycleBinPage()
            
            try:
                response = view.get(request, 1, 10)
                print(f"API响应状态: {response.status_code}")
                print(f"API响应数据: {response.data}")
            except Exception as api_error:
                print(f"❌ API调用失败: {str(api_error)}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ 没有找到用户，无法模拟API调用")
            
    except Exception as e:
        print(f"❌ API模拟测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 4. 检查URL路由
    print("\n4. 检查URL路由")
    print("-" * 40)
    
    try:
        from django.urls import reverse, NoReverseMatch
        try:
            url = reverse('dataset:recycle_bin_page', args=[1, 10])
            print(f"✅ URL路由正常: {url}")
        except NoReverseMatch:
            print("❌ URL路由配置有问题")
    except Exception as e:
        print(f"❌ URL检查失败: {str(e)}")
    
    # 5. 总结
    print("\n5. 诊断总结")
    print("-" * 40)
    
    if deleted_datasets.exists():
        print("✅ 数据库中有软删除的数据")
    else:
        print("❌ 数据库中没有软删除的数据")
    
    print("\n建议操作:")
    print("1. 如果上述测试都正常，问题可能在前端")
    print("2. 请检查浏览器Network面板中回收站API的请求和响应")
    print("3. 确认前端是否正确调用了回收站API")
    print("4. 检查前端是否正确解析了API响应")

if __name__ == "__main__":
    diagnose_recycle_bin() 