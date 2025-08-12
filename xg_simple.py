from sqlalchemy.dialects import registry
from sqlalchemy import create_engine, text


def get_input(prompt, default):
    return input(f"👉 {prompt} (默认{default}): ").strip() or default


def diagnose_xg_tables():
    host = get_input("主机地址", "127.0.0.1")
    port = get_input("端口", "5138")
    database = get_input("数据库", "SYSTEM")
    user = get_input("用户名", "SYSDBA")
    password = get_input("密码", "Fuhua0501.")
    schema = input("👉 目标Schema (留空表示当前用户): ").strip() or None

    registry.register("xg", "xg.xgPython", "dialect")
    engine_url = f"xg://{user}:{password}@{host}:{port}/{database}"

    print("\n🔗 正在尝试连接数据库...")
    print(f"主机: {host}:{port}，数据库: {database}，用户: {user}，Schema: {schema or '(当前用户)'}")
    print("=" * 60)

    try:
        engine = create_engine(engine_url)
        with engine.connect() as conn:
            print("✅ 数据库连接成功\n")

            result = conn.execute(
                text("SELECT schema_name FROM user_schemas ORDER BY schema_name")
            )
            schema_rows = result.fetchall()
            target_schemas = [row[0] for row in schema_rows]
            print("🔍 可用的Schema:", target_schemas)
            if schema:
                target_schema = schema.upper()
                result = conn.execute(
                    text("""
                        SELECT t.table_name
                        FROM dba_tables t
                        JOIN dba_schemas s
                          ON t.schema_id = s.schema_id
                          AND t.db_id = s.db_id
                        WHERE s.schema_name = :schema
                          AND t.table_name NOT LIKE 'SYS%'
                          AND t.table_name NOT LIKE 'DBA_%'
                          AND t.table_name NOT LIKE 'ALL_%'
                          AND t.table_name NOT LIKE 'USER_%'
                        ORDER BY t.table_name
                    """),
                    {"schema": target_schema},
                )
                tables_raw = result.fetchall()
                table_names = [row[0] for row in tables_raw]
            else:
                result = conn.execute(
                    text("""
                        SELECT table_name
                        FROM user_tables 
                        WHERE table_name NOT LIKE 'SYS%'
                          AND table_name NOT LIKE 'DBA_%'
                          AND table_name NOT LIKE 'ALL_%'
                          AND table_name NOT LIKE 'USER_%'
                          AND table_name NOT LIKE 'V$%'
                          AND table_name NOT LIKE 'GV$%'
                          AND table_name NOT LIKE 'X$%'
                        ORDER BY table_name
                    """)
                )
                tables_raw = result.fetchall()
                table_names = [row[0] for row in tables_raw]
                target_schema = user.upper()

            if not table_names:
                print("⚠️ 未找到任何表。")
                return

            print(f"🔍 Schema '{target_schema}' 下的表: {table_names}")
            print(f"XG: 共找到 {len(table_names)} 个表\n")

            for table_name in table_names:
                if schema:
                    result = conn.execute(
                        text("""
                            SELECT col_name, comments FROM 
                            dba_columns WHERE 
                            table_id = (
                                SELECT t.table_id FROM dba_tables t
                                JOIN dba_schemas s ON t.schema_id = s.schema_id AND t.db_id = s.db_id
                                WHERE t.table_name = :table AND s.schema_name = :schema
                            )
                            """),
                        {"schema": target_schema, "table": table_name.upper()},
                    )
                else:
                    result = conn.execute(
                        text("""
                            select col_name,comments from 
                            dba_columns where 
                            table_id=(select table_id from dba_tables 
                            where table_name= :table);
                                        """),
                        {"table": table_name.upper()},
                    )
                cols_raw = result.fetchall()
                print(cols_raw)
                print(f"\n📌 表: {table_name}")
                if not cols_raw:
                    print("  (无字段)")
                    continue
            print("  字段信息:")
            for col in cols_raw:
                col_name, comments = col
                print(f"  - {col_name} (注释: {comments or '无'})")
        print("\n🎉 所有信息输出完毕")

    except Exception as e:
        print(f"❌ 数据库连接或操作错误: {e}")


if __name__ == "__main__":
    diagnose_xg_tables()
