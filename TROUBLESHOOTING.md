# Troubleshooting - Fix lỗi Database Connection

## Lỗi: "could not translate host name"

### Nguyên nhân

Database URL không đúng hoặc database chưa sẵn sàng trên Render.

### Giải pháp

#### Bước 1: Kiểm tra Database Status

1. Đăng nhập vào Render Dashboard
2. Vào PostgreSQL database của bạn
3. Kiểm tra Status phải là **"Available"** (màu xanh)
4. Nếu đang "Creating" hoặc "Suspended", đợi cho đến khi Available

#### Bước 2: Lấy đúng Internal Database URL

**QUAN TRỌNG**: Phải dùng **Internal Database URL**, KHÔNG dùng External URL!

1. Trong Render PostgreSQL Dashboard
2. Tìm section **"Connections"**
3. Copy **"Internal Database URL"** (có dạng):

```
postgresql://user:password@dpg-xxxxx-a.oregon-postgres.render.com/dbname
```

**Lưu ý hostname**:

- ✅ Đúng: `dpg-xxxxx-a.oregon-postgres.render.com`
- ❌ Sai: `dpg-xxxxx-a` (thiếu region và domain)

#### Bước 3: Update Environment Variable

1. Vào Web Service trên Render
2. Tab **"Environment"**
3. Tìm biến `DATABASE_URL`
4. Click **"Edit"**
5. Paste Internal Database URL mới
6. Click **"Save Changes"**

Web service sẽ tự động redeploy.

#### Bước 4: Verify Connection

Sau khi redeploy xong, test connection:

1. Vào tab **"Shell"** của Web Service
2. Chạy:

```bash
python
```

```python
import os
from sqlalchemy import create_engine

# Kiểm tra DATABASE_URL
db_url = os.environ.get('DATABASE_URL')
print(f"DATABASE_URL: {db_url[:50]}...")  # In 50 ký tự đầu

# Test connection
try:
    engine = create_engine(db_url)
    conn = engine.connect()
    print("✓ Database connection successful!")
    conn.close()
except Exception as e:
    print(f"✗ Connection failed: {e}")

exit()
```

## Lỗi: "Connection timeout"

### Giải pháp

Database có thể đang quá tải hoặc sleep (nếu dùng Free tier).

1. Restart database:

   - Vào PostgreSQL Dashboard
   - Click "Suspend" rồi "Resume"

2. Hoặc restart Web Service:
   - Vào Web Service Dashboard
   - Manual Deploy → "Clear build cache & deploy"

## Lỗi: "Authentication failed"

### Nguyên nhân

Database credentials sai.

### Giải pháp

1. Tạo lại database connection string:

   - Username: Lấy từ PostgreSQL Dashboard
   - Password: Lấy từ PostgreSQL Dashboard
   - Host: Lấy từ Internal Database URL
   - Database name: Lấy từ PostgreSQL Dashboard

2. Format đúng:

```
postgresql://username:password@host:5432/database_name
```

## Sử dụng SQLite cho Development

Nếu bạn chỉ đang test local và không cần PostgreSQL:

1. **Không set** biến `DATABASE_URL`
2. App sẽ tự động dùng SQLite: `sqlite:///students.db`

Trong file `.env`:

```bash
# Comment out hoặc xóa dòng này
# DATABASE_URL=postgresql://...

# Chỉ cần SECRET_KEY
SECRET_KEY=your-secret-key-here
```

Hoặc trong code, đảm bảo có fallback:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///students.db'  # Fallback to SQLite
)
```

## Test Database Connection trước khi Deploy

Tạo file `test_db.py`:

```python
import os
from sqlalchemy import create_engine, text

def test_connection():
    db_url = os.environ.get('DATABASE_URL')

    if not db_url:
        print("❌ DATABASE_URL not set!")
        return False

    print(f"Testing connection to: {db_url[:50]}...")

    try:
        # Fix postgres:// to postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)

        engine = create_engine(db_url, connect_args={'connect_timeout': 10})

        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected successfully!")
            print(f"PostgreSQL version: {version[:50]}...")
            return True

    except Exception as e:
        print(f"❌ Connection failed!")
        print(f"Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_connection()
```

Chạy local:

```bash
export DATABASE_URL="postgresql://..."  # Paste your URL
python test_db.py
```

## Fix cho Render Deployment

### 1. Đảm bảo Database và Web Service cùng Region

- PostgreSQL: Singapore
- Web Service: Singapore

Nếu khác region, tạo lại database trong cùng region với Web Service.

### 2. Kiểm tra Network

Internal Database URL chỉ hoạt động khi:

- Web Service và Database cùng account Render
- Cùng region
- Database status là "Available"

### 3. Thêm Health Check

Trong `app.py`, thêm endpoint để check database:

```python
@app.route('/health')
def health():
    try:
        # Try to execute a simple query
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
```

Sau đó test:

```bash
curl https://your-app.onrender.com/health
```

## Common Mistakes

❌ **Sai:**

```python
DATABASE_URL=dpg-xxxxx-a  # Thiếu protocol và domain
DATABASE_URL=postgres://...  # Dùng postgres:// thay vì postgresql://
DATABASE_URL=<External URL>  # Dùng External thay vì Internal
```

✅ **Đúng:**

```python
DATABASE_URL=postgresql://user:pass@dpg-xxxxx-a.oregon-postgres.render.com:5432/dbname
# Hoặc
DATABASE_URL=postgresql+psycopg2://user:pass@dpg-xxxxx-a.oregon-postgres.render.com:5432/dbname
```

## Logs để Debug

Xem logs trong Render:

1. Vào Web Service Dashboard
2. Tab "Logs"
3. Tìm dòng:

```
sqlalchemy.exc.OperationalError
psycopg2.OperationalError
```

Nếu thấy:

- `Name or service not known` → Hostname sai
- `timeout` → Database chưa sẵn sàng hoặc quá tải
- `authentication failed` → Password sai
- `database does not exist` → Database name sai

## Quick Fix Checklist

- [ ] Database status là "Available"
- [ ] Dùng Internal Database URL (không phải External)
- [ ] DATABASE_URL có đầy đủ: protocol, username, password, host, port, database name
- [ ] Web Service và Database cùng region
- [ ] Đã save Environment Variables và redeploy
- [ ] Không có typo trong database URL
- [ ] `postgresql://` hoặc `postgresql+psycopg2://` (không phải `postgres://`)

## Nếu vẫn không được

### Plan B: Tạo Database mới

1. Xóa database cũ (nếu không có dữ liệu quan trọng)
2. Tạo database mới:

   - Name: `student-db-v2`
   - Same region với Web Service
   - PostgreSQL 15

3. Copy **Internal Database URL** mới
4. Update `DATABASE_URL` trong Web Service
5. Chờ redeploy
6. Chạy `init_db.py` để tạo tables

### Plan C: Dùng SQLite tạm thời

Nếu chỉ cần demo:

1. Xóa `DATABASE_URL` khỏi Environment Variables
2. App sẽ tự động dùng SQLite
3. Data sẽ mất khi restart (Free tier)
4. Không khuyến khích cho production

## Contact Support

Nếu đã thử tất cả vẫn không được:

1. Check Render Status: https://status.render.com
2. Render Community: https://community.render.com
3. File support ticket (nếu dùng paid plan)

## Prevention

Để tránh lỗi này trong tương lai:

1. ✅ Luôn verify Database URL trước khi deploy
2. ✅ Test connection với `test_db.py`
3. ✅ Monitor database status regularly
4. ✅ Setup alerts cho downtime
5. ✅ Backup database thường xuyên
6. ✅ Document DATABASE_URL format cho team
