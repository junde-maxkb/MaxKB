#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回收站功能测试脚本
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
from django.utils import timezone
from datetime import timedelta

def test_recycle_bin_functionality():
    """测试回收站功能"""
    print("开始测试回收站功能...")
    
    # 1. 检查是否有知识库数据
    datasets = DataSet.objects.all()
    print(f"当前知识库总数: {datasets.count()}")
    
    # 2. 检查软删除字段是否存在
    deleted_datasets = DataSet.objects.filter(is_deleted=True)
    print(f"已删除的知识库数量: {deleted_datasets.count()}")
    
    # 3. 检查正常知识库数量
    active_datasets = DataSet.objects.filter(is_deleted=False)
    print(f"正常知识库数量: {active_datasets.count()}")
    
    # 4. 显示一些已删除的知识库信息
    if deleted_datasets.exists():
        print("\n已删除的知识库列表:")
        for dataset in deleted_datasets[:5]:  # 只显示前5个
            delete_time = dataset.delete_time.strftime('%Y-%m-%d %H:%M:%S') if dataset.delete_time else '未知'
            print(f"  - {dataset.name} (ID: {dataset.id}) - 删除时间: {delete_time}")
    else:
        print("\n当前没有已删除的知识库")
    
    # 5. 测试软删除功能（如果有正常知识库）
    if active_datasets.exists():
        test_dataset = active_datasets.first()
        print(f"\n测试软删除功能:")
        print(f"  测试知识库: {test_dataset.name} (ID: {test_dataset.id})")
        
        # 模拟软删除
        test_dataset.is_deleted = True
        test_dataset.delete_time = timezone.now()
        test_dataset.save()
        print(f"  已软删除知识库: {test_dataset.name}")
        
        # 验证软删除
        deleted_count = DataSet.objects.filter(is_deleted=True).count()
        print(f"  软删除后，已删除知识库数量: {deleted_count}")
        
        # 恢复知识库
        test_dataset.is_deleted = False
        test_dataset.delete_time = None
        test_dataset.save()
        print(f"  已恢复知识库: {test_dataset.name}")
        
        # 验证恢复
        active_count = DataSet.objects.filter(is_deleted=False).count()
        print(f"  恢复后，正常知识库数量: {active_count}")
    else:
        print("\n没有可用的知识库进行测试")
    
    print("\n回收站功能测试完成!")

if __name__ == "__main__":
    test_recycle_bin_functionality() 