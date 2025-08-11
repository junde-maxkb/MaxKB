import sys
import traceback

try:
    from sqlalchemy import create_engine, text
    import dmPython

    print("✅ 成功导入 dmPython 和 sqlalchemy")
except ImportError:
    print("❌ 导入dmPython失败，请确保已安装DM数据库的Python驱动")
    print("请先安装: pip install dmPython sqlalchemy")
    sys.exit(1)


def diagnose_dm_tables():
    print("=" * 60)
    print("达梦数据库表诊断工具")
    print("=" * 60)

    # 获取连接信息
    host = input("👉 主机地址 (默认127.0.0.1): ").strip() or "127.0.0.1"
    port = input("👉 端口 (默认5236): ").strip() or "5238"
    user = input("👉 用户名 (默认SYSDBA): ").strip() or "SYSDBA"
    password = input("👉 密码: ").strip() or "Fuhua0501."
    schema = input("👉 目标Schema: ").strip() or None

    conn_url = f"dm+dmPython://{user}:{password}@{host}:{port}"

    print("\n🔗 正在尝试连接数据库...")
    print(f"主机: {host}:{port}")
    print(f"用户: {user}")
    print(f"目标Schema: {schema if schema else '(当前用户)'}")
    print("=" * 60)

    try:
        engine = create_engine(conn_url, pool_pre_ping=True, pool_timeout=30, echo=False)

        with engine.begin() as conn:
            print("✅ 数据库连接成功\n")
            result = conn.execute(text("SELECT username FROM dba_users"))
            schemas = [row[0] for row in result]
            print("可用的 Schema 列表:", schemas)

            # 当前用户
            print("1️⃣ 当前连接用户:")
            current_user = conn.execute(text("SELECT USER FROM DUAL")).scalar()
            print(f"   当前用户: {current_user}\n")

            # 查询当前用户拥有的所有 schema
            res = conn.execute(text("""
                SELECT SCH.NAME AS schema_name
                  FROM SYSOBJECTS SCH
                  JOIN DBA_USERS U
                    ON SCH.PID = U.USER_ID
                 WHERE SCH.TYPE$ = 'SCH'
                   AND U.USERNAME = :user
                 ORDER BY SCH.NAME
            """), {'user': current_user.upper()})
            user_schemas = [row[0] for row in res]
            print(f"🔍 用户 '{current_user}' 拥有的 schema: {user_schemas}\n")

            # 确定目标 schema
            target_schema = schema.upper() if schema else current_user.upper()

            # 如果输入的 target_schema 不在该列表内，提醒并重设
            if schema and target_schema not in user_schemas:
                print(f"⚠️ 警告: 用户 '{current_user}' 不拥有 schema '{target_schema}'。")
                print(f"   默认切换为 {user_schemas[0]}（默认模式）")
                target_schema = user_schemas[0]

            # 检查 Schema 是否存在
            print(f"2️⃣ 检查 Schema（用户） '{target_schema}' 是否存在:")
            exists = conn.execute(
                text("SELECT COUNT(*) FROM dba_users WHERE username = :schema"),
                {'schema': target_schema}
            ).scalar()
            if exists:
                print(f"   ✅ Schema '{target_schema}' 存在\n")
            else:
                print(f"   ❌ Schema '{target_schema}' 不存在，请检查输入\n")
                return

            print(f"3️⃣ 列出 Schema '{target_schema}' 下的所有表:")
            if schema:
                tables = conn.execute(
                    text("""
                        SELECT table_name FROM all_tables 
                        WHERE owner = :schema 
                        AND table_name NOT LIKE 'SYS%'
                        AND table_name NOT LIKE 'DBA_%'
                        AND table_name NOT LIKE 'ALL_%'
                        AND table_name NOT LIKE 'USER_%'
                        AND table_name NOT LIKE 'V$%'
                        AND table_name NOT LIKE 'GV$%'
                        AND table_name NOT LIKE 'X$%'
                        AND owner NOT IN ('SYS', 'SYSTEM', 'SYSDBA')
                        ORDER BY table_name
                    """),
                    {'schema': target_schema}
                ).fetchall()
            else:
                tables = conn.execute(
                    text("""
                        SELECT table_name FROM user_tables 
                        WHERE table_name NOT LIKE 'SYS%'
                        AND table_name NOT LIKE 'DBA_%'
                        AND table_name NOT LIKE 'ALL_%'
                        AND table_name NOT LIKE 'USER_%'
                        AND table_name NOT LIKE 'V$%'
                        AND table_name NOT LIKE 'GV$%'
                        AND table_name NOT LIKE 'X$%'
                        ORDER BY table_name
                    """)
                ).fetchall()
            print("tables:", tables)
            if tables:
                for row in tables:
                    table_name = row[0]
                    if table_name.startswith('#'):
                        print(f"🟡 临时表: {table_name}")
                        continue
                    print(f"   📋 {table_name}")
            else:
                print("(无表)")

            print(f"\n✅ 共计 {len(tables)} 个表\n")

            if schema:
                tab_comments = conn.execute(
                    text("SELECT table_name, comments FROM all_tab_comments WHERE owner = :schema"),
                    {'schema': target_schema}
                ).fetchall()
            else:
                tab_comments = conn.execute(
                    text("SELECT table_name, comments FROM user_tab_comments")
                ).fetchall()
            tab_comment_map = {t: c for t, c in tab_comments}

            print(f"4️⃣ 获取 Schema '{target_schema}' 下所有表的列信息、注释:")
            for table_name, in tables:
                if table_name.startswith('#'):
                    continue
                print(f"\n表: {table_name}")
                if table_name in tab_comment_map and tab_comment_map[table_name]:
                    print(f"📝 表注释: {tab_comment_map[table_name]}")
                # 获取列和列注释 - 修正：加上owner过滤
                if schema:
                    cols = conn.execute(
                        text("""
                            SELECT column_name, data_type, data_length 
                            FROM all_tab_columns 
                            WHERE owner = :schema AND table_name = :table
                            ORDER BY column_id
                        """),
                        {"schema": target_schema, "table": table_name}
                    ).fetchall()
                    col_comments = conn.execute(
                        text("""
                            SELECT column_name, comments 
                            FROM all_col_comments 
                            WHERE owner = :schema AND table_name = :table
                        """),
                        {"schema": target_schema, "table": table_name}
                    ).fetchall()
                else:
                    cols = conn.execute(
                        text("""
                            SELECT column_name, data_type, data_length 
                            FROM user_tab_columns 
                            WHERE table_name = :table
                            ORDER BY column_id
                        """),
                        {"table": table_name}
                    ).fetchall()
                    col_comments = conn.execute(
                        text("""
                            SELECT column_name, comments 
                            FROM user_col_comments 
                            WHERE table_name = :table
                        """),
                        {"table": table_name}
                    ).fetchall()
                comment_map = {col: cm for col, cm in col_comments}

                if cols:
                    for col_name, data_type, data_length in cols:
                        cm = comment_map.get(col_name)
                        info = f"- 列名: {col_name}, 类型: {data_type}, 长度: {data_length}"
                        if cm:
                            info += f", 注释: {cm}"
                        print(info)
                else:
                    print("   (无列信息)")

            print("\n✅ 所有表信息（含表注释 + 列注释）输出完毕")

    except Exception as e:
        print(f"❌ 出现错误: {e}\n")
        traceback.print_exc()
        print("\n请检查：")
        print("1. DM服务是否启动")
        print("2. 网络地址/端口是否正确")
        print("3. 用户名和密码是否正确")
        print("4. 用户权限是否足够")


if __name__ == "__main__":
    diagnose_dm_tables()
