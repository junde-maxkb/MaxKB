#!/usr/bin/env python3
"""
简化版Oracle表获取诊断脚本
不依赖Django环境，直接测试Oracle连接和表获取
"""

try:
    import oracledb
    from sqlalchemy import create_engine, text
    print("✅ 导入oracledb和sqlalchemy成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请先安装: pip install oracledb sqlalchemy")
    exit(1)

def diagnose_oracle_tables():
    """简化版Oracle表获取诊断"""
    
    print("=" * 60)
    print("Oracle 表获取诊断工具 (简化版)")
    print("=" * 60)
    
    # 获取连接信息
    print("请输入Oracle连接信息:")
    host = input("主机地址 (默认localhost): ").strip() or "localhost"
    port = input("端口 (默认1521): ").strip() or "1521"
    user = input("用户名: ").strip()
    password = input("密码: ").strip()
    sid_or_service = input("SID或Service Name: ").strip()
    connect_type = input("连接类型 (sid/service, 默认sid): ").strip() or "sid"
    schema = input("目标Schema (user_001): ").strip() or None
    
    # 构建连接URI
    if connect_type.lower() == 'sid':
        uri = f"oracle+oracledb://{user}:{password}@{host}:{port}/{sid_or_service}"
    else:
        uri = f"oracle+oracledb://{user}:{password}@{host}:{port}/?service_name={sid_or_service}"
    
    print(f"\n连接信息:")
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
            
            # 2. 检查目标Schema是否存在
            if schema:
                schema_upper = schema.upper()
                print(f"2️⃣ 检查Schema '{schema_upper}' 是否存在:")
                result = conn.execute(text("SELECT COUNT(*) FROM all_users WHERE username = :schema"), 
                                    {'schema': schema_upper})
                schema_exists = result.fetchone()[0] > 0
                if schema_exists:
                    print(f"   ✅ Schema '{schema_upper}' 存在")
                else:
                    print(f"   ❌ Schema '{schema_upper}' 不存在")
                    print(f"   提示: DBeaver显示的小写schema可能对应大写的Oracle schema")
                    print(f"   建议检查: USER_001, USR_001 等变体")
                print()
            
            # 3. 检查Schema下的所有表（无过滤）
            if schema:
                schema_upper = schema.upper()
                print(f"3️⃣ Schema '{schema_upper}' 下的所有表（无过滤）:")
                result = conn.execute(text("SELECT table_name FROM all_tables WHERE owner = :schema ORDER BY table_name"), 
                                    {'schema': schema_upper})
                all_tables = [row[0] for row in result]
                if all_tables:
                    for table in all_tables:
                        print(f"   📋 {table}")
                else:
                    print("   (无表)")
                print(f"   总计: {len(all_tables)} 个表")
                print()
                
                # 4. 执行MaxKB的实际查询逻辑（有Schema）
                print("4️⃣ MaxKB实际执行的查询 (有Schema):")
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
                maxkb_tables = [row[0] for row in result]
                
                if maxkb_tables:
                    for table in maxkb_tables:
                        print(f"   ✅ {table}")
                else:
                    print("   ❌ 无表 (可能被过滤条件排除)")
                
                print(f"   MaxKB找到: {len(maxkb_tables)} 个表")
                print()
                
                # 5. 分析被过滤的表
                if all_tables and not maxkb_tables:
                    print("5️⃣ 分析被过滤的表:")
                    for table in all_tables:
                        print(f"   检查表: {table}")
                        # 检查各个过滤条件
                        filters = [
                            ('以$结尾', table.endswith('$')),
                            ('LOGMNR_开头', table.startswith('LOGMNR_')),
                            ('SYS_开头', table.startswith('SYS_')),
                            ('APEX_开头', table.startswith('APEX_')),
                            ('FLOWS_开头', table.startswith('FLOWS_')),
                            ('MVIEW$开头', table.startswith('MVIEW$')),
                            ('其他系统表模式', any([
                                table.startswith('SQLPLUS_'),
                                table.startswith('MDRS_'),
                                table.startswith('MDXT_'),
                                table.startswith('WRI$'),
                                table.startswith('PLAN_TABLE'),
                                table.startswith('BIN$'),
                                table.startswith('DR$'),
                                table == 'DUAL'
                            ]))
                        ]
                        
                        matched_filters = [f[0] for f in filters if f[1]]
                        if matched_filters:
                            print(f"     ❌ 被过滤原因: {', '.join(matched_filters)}")
                        else:
                            print(f"     ⚠️  应该显示 - 可能是MaxKB的bug")
                            
            else:
                # 无Schema时查询当前用户表
                print("3️⃣ 当前用户的表:")
                result = conn.execute(text("SELECT table_name FROM user_tables ORDER BY table_name"))
                user_tables = [row[0] for row in result]
                if user_tables:
                    for table in user_tables:
                        print(f"   📋 {table}")
                else:
                    print("   (当前用户无表)")
                print(f"   总计: {len(user_tables)} 个表")
                
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("请检查:")
        print("1. Oracle服务是否启动")
        print("2. 连接参数是否正确")
        print("3. 用户权限是否充足")

if __name__ == "__main__":
    diagnose_oracle_tables() 