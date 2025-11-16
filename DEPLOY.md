# Hướng dẫn Deploy lên Render với Docker

## Chuẩn bị

### 1. Tạo tài khoản Render

- Truy cập: https://render.com
- Đăng ký tài khoản miễn phí
- Liên kết với GitHub account

### 2. Chuẩn bị GitHub Repository

```bash
# Khởi tạo Git repository
git init
git add .
git commit -m "Initial commit"

# Tạo repository trên GitHub và push code
git remote add origin https://github.com/yourusername/student-management.git
git branch -M main
git push -u origin main
```

## Bước 1: Tạo PostgreSQL Database

1. Đăng nhập vào Render Dashboard
2. Click **"New +"** → **"PostgreSQL"**
3. Điền thông tin:

```
Name: student-db
Database: studentdb
User: studentuser
Region: Singapore (closest to Vietnam)
PostgreSQL Version: 15
Instance Type: Free
```

4. Click **"Create Database"**
5. Đợi database được tạo (khoảng 1-2 phút)
6. **Quan trọng**: Copy **Internal Database URL** có dạng:

```
postgresql://studentuser:xxxxx@dpg-xxxxx-singapore-postgres.render.com/studentdb
```

## Bước 2: Deploy Web Service

### 2.1. Tạo Web Service

1. Trong Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect repository từ GitHub:
   - Chọn repository: `student-management`
   - Click **"Connect"**

### 2.2. Cấu hình Web Service

Điền các thông tin sau:

```
Name: student-management
Region: Singapore
Branch: main
Runtime: Docker
Instance Type: Free
```

### 2.3. Thiết lập Environment Variables

Trong phần **Environment**, thêm các biến:

1. Click **"Add Environment Variable"**

2. Thêm `DATABASE_URL`:

```
Key: DATABASE_URL
Value: <paste Internal Database URL từ Bước 1>
```

3. Thêm `SECRET_KEY`:

```
Key: SECRET_KEY
Value: <tạo một chuỗi random 32 ký tự>
```

**Cách tạo SECRET_KEY random:**

```bash
# Trên Linux/Mac:
python -c "import secrets; print(secrets.token_hex(32))"

# Hoặc dùng online: https://randomkeygen.com/
```

4. (Optional) Thêm các biến khác nếu cần:

```
Key: FLASK_ENV
Value: production
```

### 2.4. Deploy

1. Click **"Create Web Service"**
2. Đợi build process hoàn thành (5-10 phút cho lần đầu)
3. Theo dõi logs trong tab **"Logs"**

## Bước 3: Khởi tạo Database

Sau khi deploy thành công, bạn cần khởi tạo database:

### Phương án 1: Dùng Shell trên Render

1. Vào Web Service vừa tạo
2. Click tab **"Shell"**
3. Chạy lệnh:

```bash
python init_db.py
```

### Phương án 2: Dùng Python console

Trong Shell, chạy:

```bash
python
```

Sau đó:

```python
from app import app, db, User

with app.app_context():
    # Tạo tables
    db.create_all()

    # Tạo admin user
    admin = User(
        username='admin',
        role='admin',
        full_name='Administrator',
        email='admin@example.com'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print("Database initialized!")

exit()
```

## Bước 4: Kiểm tra

1. Truy cập URL được cung cấp bởi Render (dạng: `https://student-management-xxxx.onrender.com`)
2. Đăng nhập với:
   - Username: `admin`
   - Password: `admin123`

## Bước 5: Bảo mật

⚠️ **QUAN TRỌNG - Làm ngay sau khi deploy:**

### 5.1. Đổi mật khẩu admin

1. Vào Shell trên Render
2. Chạy:

```python
from app import app, db, User

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    admin.set_password('your-new-strong-password')
    db.session.commit()
    print("Password changed!")
```

### 5.2. Xóa dữ liệu mẫu (nếu có)

```python
from app import app, db, Student, Subject, Score

with app.app_context():
    # Xóa điểm mẫu
    Score.query.delete()
    # Xóa sinh viên mẫu
    Student.query.delete()
    # Xóa môn học mẫu
    Subject.query.delete()
    db.session.commit()
    print("Sample data cleared!")
```

## Troubleshooting

### Lỗi: "Application failed to respond"

**Nguyên nhân**: Container chưa start hoàn toàn

**Giải pháp**:

- Đợi thêm 1-2 phút
- Check logs để xem lỗi cụ thể
- Restart service nếu cần

### Lỗi: "Database connection failed"

**Nguyên nhân**: `DATABASE_URL` sai hoặc database chưa sẵn sàng

**Giải pháp**:

1. Kiểm tra database có status "Available" không
2. Verify `DATABASE_URL` trong Environment Variables
3. Đảm bảo dùng **Internal Database URL**, không phải External

### Lỗi: "502 Bad Gateway"

**Nguyên nhân**: Service đang build hoặc crashed

**Giải pháp**:

1. Kiểm tra tab "Events" để xem build status
2. Xem logs để tìm lỗi
3. Nếu build failed, check Dockerfile và requirements.txt

### Lỗi: "OSError: [Errno 98] Address already in use"

**Nguyên nhân**: Port conflict trong Dockerfile

**Giải pháp**: Đảm bảo Dockerfile dùng đúng port (5000)

### Database bị reset sau mỗi lần deploy

**Nguyên nhân**: Đang dùng SQLite trong container

**Giải pháp**: Đảm bảo đã set `DATABASE_URL` đến PostgreSQL database

## Auto Deploy

Mặc định, Render sẽ tự động deploy khi bạn push code mới lên GitHub.

Để tắt auto deploy:

1. Vào Web Service settings
2. Tìm "Auto-Deploy"
3. Chọn "No"

Để deploy thủ công:

1. Vào tab "Manual Deploy"
2. Click "Deploy latest commit"

## Monitoring

### Xem Logs

- Tab "Logs" trong Web Service
- Real-time logs của ứng dụng

### Xem Metrics

- Tab "Metrics"
- CPU, Memory, Request count

### Alerts

- Có thể setup email alerts khi service down
- Vào Settings → Notifications

## Scaling (Paid plans)

Free plan có giới hạn:

- 750 hours/month
- Sleep after 15 mins inactive
- Wake up on request (có thể chậm ~30s)

Để upgrade:

1. Vào Settings
2. Chọn Instance Type khác (Starter, Standard, Pro)
3. Paid plans không sleep và có nhiều resources hơn

## Backup Database

### Manual Backup

1. Vào PostgreSQL database
2. Tab "Backups"
3. Click "Create Backup"

### Restore Backup

1. Tab "Backups"
2. Chọn backup cần restore
3. Click "Restore"

### Download Database

```bash
# Cài pg_dump trên máy local
# macOS: brew install postgresql
# Ubuntu: apt-get install postgresql-client

# Export database
pg_dump <EXTERNAL_DATABASE_URL> > backup.sql

# Import database
psql <EXTERNAL_DATABASE_URL> < backup.sql
```

## Domain tùy chỉnh

Free plan hỗ trợ custom domain:

1. Vào Settings → Custom Domain
2. Thêm domain của bạn
3. Cấu hình DNS records theo hướng dẫn
4. SSL certificate sẽ tự động được cấp

## Tips & Best Practices

✅ **DO:**

- Dùng strong passwords
- Regularly backup database
- Monitor logs for errors
- Keep dependencies updated
- Use environment variables cho sensitive data

❌ **DON'T:**

- Hardcode passwords trong code
- Commit .env file vào Git
- Dùng admin/admin123 trong production
- Expose Internal Database URL publicly

## Cập nhật Code

```bash
# Trên local machine
git add .
git commit -m "Update features"
git push origin main

# Render sẽ tự động detect và deploy
# Hoặc deploy thủ công trên dashboard
```

## Chi phí

**Free Tier bao gồm:**

- 1 Web Service
- 1 PostgreSQL Database (1 GB storage)
- 750 hours/month shared
- 100 GB bandwidth

**Lưu ý**: Multiple services chia sẻ 750 hours

## Support

Nếu gặp vấn đề:

1. Check documentation: https://render.com/docs
2. Community forum: https://community.render.com
3. Support tickets (Paid plans)

## Checklist sau khi Deploy

- [ ] Application chạy được
- [ ] Database connected
- [ ] Đăng nhập được
- [ ] Đổi mật khẩu admin
- [ ] Test các chức năng chính
- [ ] Setup monitoring/alerts
- [ ] Backup database
- [ ] Document URL và credentials
- [ ] (Optional) Setup custom domain

🎉 **Chúc bạn deploy thành công!**
