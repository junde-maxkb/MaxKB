#!/usr/bin/env python3
"""
Oracle表获取诊断脚本
用于排查MaxKB无法获取Oracle表的问题
"""

import os
import sys
import django
from sqlalchemy import create_engine, text

# 设置Django环境
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartdoc.settings.dev')
django.setup()

def diagnose_oracle_tables(host, port, user, password, sid_or_service, schema=None, connect_type='sid'):
    """诊断Oracle表获取问题"""
    
    print("=" * 60)
    print("Oracle 表获取诊断工具")
    print("=" * 60)
    
    # 构建连接URI
    if connect_type == 'sid':
        uri = f"oracle+oracledb://{user}:{password}@{host}:{port}/{sid_or_service}"
    else:
        uri = f"oracle+oracledb://{user}:{password}@{host}:{port}/?service_name={sid_or_service}"
    
    print(f"连接信息:")
    print(f"  主机: {host}:{port}")
    print(f"  用户: {user}")
    print(f"  {connect_type}: {sid_or_service}")
    print(f"  目标Schema: {schema if schema else '(当前用户)'}")
    print()
    
    try:
        # 创建连接
        engine = create_engine(uri, pool_pre_ping=True, pool_timeout=30, echo=False)
        
        with engine.connect() as conn:
            print("✅ 数据库连接成功")
            print()
            
            # 1. 检查当前用户
            print("1️⃣ 检查当前连接用户:")
            result = conn.execute(text("SELECT USER FROM DUAL"))
            current_user = result.fetchone()[0]
            print(f"   当前用户: {current_user}")
            print()
            
            # 2. 检查所有Schema
            print("2️⃣ 可用的Schema列表:")
            result = conn.execute(text("SELECT username FROM all_users ORDER BY username"))
            all_schemas = [row[0] for row in result]
            for s in all_schemas[:10]:  # 显示前10个
                print(f"   {s}")
            if len(all_schemas) > 10:
                print(f"   ... 还有 {len(all_schemas) - 10} 个")
            print()
            
            # 3. 检查目标Schema是否存在
            if schema:
                schema_upper = schema.upper()
                if schema_upper in all_schemas:
                    print(f"✅ 目标Schema '{schema_upper}' 存在")
                else:
                    print(f"❌ 目标Schema '{schema_upper}' 不存在")
                    print(f"   提示: DBeaver中显示的可能是小写，但Oracle存储为大写")
                    # 模糊匹配
                    matches = [s for s in all_schemas if schema.upper() in s or s in schema.upper()]
                    if matches:
                        print(f"   可能的匹配: {matches}")
                print()
            
            # 4. 检查Schema下的所有表（无过滤）
            if schema:
                schema_upper = schema.upper()
                print(f"3️⃣ Schema '{schema_upper}' 下的所有表（无过滤）:")
                result = conn.execute(text("SELECT table_name FROM all_tables WHERE owner = :schema"), 
                                    {'schema': schema_upper})
                all_tables = [row[0] for row in result]
                if all_tables:
                    for table in all_tables:
                        print(f"   {table}")
                else:
                    print("   (无表)")
                print(f"   总计: {len(all_tables)} 个表")
                print()
            
            # 5. 执行MaxKB的实际查询逻辑
            print("4️⃣ MaxKB实际执行的查询:")
            if schema:
                schema_upper = schema.upper()
                print(f"   查询指定schema '{schema_upper}' 下的表")
                maxkb_query = text("""
                    SELECT table_name FROM all_tables 
                    WHERE owner = :schema_name
                    AND table_name NOT LIKE 'LOGMNR_%'
                    AND table_name NOT LIKE 'SYS_%'
                    AND table_name NOT LIKE 'APEX_%' 
                    AND table_name NOT LIKE 'FLOWS_%'
                    AND table_name NOT LIKE 'MVIEW$%'
                    AND table_name NOT LIKE 'SQLPLUS_%'
                    AND table_name NOT LIKE 'MDRS_%'
                    AND table_name NOT LIKE 'MDXT_%'
                    AND table_name NOT LIKE 'WRI$%'
                    AND table_name NOT LIKE 'PLAN_TABLE%'
                    AND table_name NOT LIKE '%$'
                    AND table_name NOT LIKE 'BIN$%'
                    AND table_name NOT LIKE 'DR$%'
                    AND table_name NOT IN ('DUAL')
                    ORDER BY table_name
                """)
                result = conn.execute(maxkb_query, {'schema_name': schema_upper})
            else:
                print("   查询当前用户的表")
                maxkb_query = text("""
                    SELECT table_name FROM user_tables 
                    WHERE table_name NOT LIKE 'LOGMNR_%'
                    AND table_name NOT LIKE 'SYS_%'
                    AND table_name NOT LIKE 'APEX_%' 
                    AND table_name NOT LIKE 'FLOWS_%'
                    AND table_name NOT LIKE 'MVIEW$%'
                    AND table_name NOT LIKE 'SQLPLUS_%'
                    AND table_name NOT LIKE 'MDRS_%'
                    AND table_name NOT LIKE 'MDXT_%'
                    AND table_name NOT LIKE 'WRI$%'
                    AND table_name NOT LIKE 'PLAN_TABLE%'
                    AND table_name NOT LIKE '%$'
                    AND table_name NOT LIKE 'BIN$%'
                    AND table_name NOT LIKE 'DR$%'
                    AND table_name NOT IN ('DUAL')
                    ORDER BY table_name
                """)
                result = conn.execute(maxkb_query)
            
            maxkb_tables = [row[0] for row in result]
            if maxkb_tables:
                for table in maxkb_tables:
                    print(f"   ✅ {table}")
            else:
                print("   ❌ 无表 (可能被过滤条件排除)")
            
            print(f"   MaxKB找到: {len(maxkb_tables)} 个表")
            print()
            
            # 6. 分析过滤掉的表
            if schema and all_tables and not maxkb_tables:
                print("5️⃣ 分析被过滤的表:")
                for table in all_tables:
                    print(f"   检查表: {table}")
                    # 检查各个过滤条件
                    filters = [
                        ('LOGMNR_%', table.startswith('LOGMNR_')),
                        ('SYS_%', table.startswith('SYS_')),
                        ('APEX_%', table.startswith('APEX_')),
                        ('FLOWS_%', table.startswith('FLOWS_')),
                        ('MVIEW$%', table.startswith('MVIEW$')),
                        ('SQLPLUS_%', table.startswith('SQLPLUS_')),
                        ('MDRS_%', table.startswith('MDRS_')),
                        ('MDXT_%', table.startswith('MDXT_')),
                        ('WRI$%', table.startswith('WRI$')),
                        ('PLAN_TABLE%', table.startswith('PLAN_TABLE')),
                        ('%$', table.endswith('$')),
                        ('BIN$%', table.startswith('BIN$')),
                        ('DR$%', table.startswith('DR$')),
                        ('DUAL', table == 'DUAL'),
                    ]
                    
                    matched_filters = [f[0] for f in filters if f[1]]
                    if matched_filters:
                        print(f"     ❌ 被过滤: {matched_filters}")
                    else:
                        print(f"     ✅ 应该显示")
            
        print("=" * 60)
        print("诊断完成")
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")

if __name__ == "__main__":
    print("请按提示输入Oracle连接信息:")
    host = input("主机地址 (默认localhost): ").strip() or "localhost"
    port = input("端口 (默认1521): ").strip() or "1521"
    user = input("用户名: ").strip()
    password = input("密码: ").strip()
    sid_or_service = input("SID或Service Name: ").strip()
    connect_type = input("连接类型 (sid/service, 默认sid): ").strip() or "sid"
    schema = input("目标Schema (可选): ").strip() or None
    
    diagnose_oracle_tables(host, port, user, password, sid_or_service, schema, connect_type) 