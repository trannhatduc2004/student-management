import psycopg2

try:
    conn = psycopg2.connect(
        host="dpg-d4d2isodl3ps73bqj0u0-a.singapore-postgres.render.com",
        port=5432,
        database="studentdb_6y1w",
        user="studentuser",
        password="8FsUcHcGpkIgJmhhud7Ti5Zusy58xBh6",
        sslmode="prefer"
    )
    print("✅ Kết nối thành công!")
    conn.close()
except Exception as e:
    print(f"❌ Lỗi: {e}")
