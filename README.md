# Hệ thống Quản lý Sinh viên

## Tính năng chính

✅ **Quản lý sinh viên**: CRUD đầy đủ, tìm kiếm
✅ **Quản lý môn học**: Thêm/sửa môn học, tín chỉ
✅ **Quản lý điểm số**: Nhập điểm, tính GPA tự động
✅ **Import/Export Excel**: Nhập hàng loạt, xuất báo cáo
✅ **Phân quyền**: Admin, Giáo viên, Sinh viên
✅ **Dashboard**: Thống kê với biểu đồ
✅ **Responsive**: Giao diện đẹp, dễ sử dụng

## Công nghệ sử dụng

- **Backend**: Flask + SQLAlchemy
- **Frontend**: Bootstrap 5 + Chart.js
- **Database**: PostgreSQL (production) / SQLite (development)
- **Deploy**: Docker + Render

## Cấu trúc thư mục

```
student-management/
├── app.py                  # Main application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── README.md              # Documentation
└── templates/             # HTML templates
    ├── base.html
    ├── login.html
    ├── admin_dashboard.html
    ├── teacher_dashboard.html
    ├── student_dashboard.html
    ├── students.html
    ├── add_student.html
    ├── edit_student.html
    ├── subjects.html
    ├── add_subject.html
    ├── scores.html
    ├── add_score.html
    └── import_students.html
```

## Cài đặt Local

### 1. Clone project

```bash
git clone <your-repo-url>
cd student-management
```

### 2. Tạo virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Chạy ứng dụng

```bash
python app.py
```

Truy cập: http://localhost:5000

**Tài khoản mặc định:**

- Username: `admin`
- Password: `admin123`

## Deploy lên Render

### Bước 1: Chuẩn bị Repository

1. Tạo repository trên GitHub
2. Push code lên:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Bước 2: Tạo PostgreSQL Database trên Render

1. Đăng nhập vào [Render](https://render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Điền thông tin:
   - **Name**: `student-db` (hoặc tên bạn muốn)
   - **Database**: `studentdb`
   - **User**: `studentuser`
   - **Region**: Singapore (gần Việt Nam nhất)
   - **Plan**: Free
4. Click **"Create Database"**
5. **Lưu lại Internal Database URL** (dạng `postgresql://...`)

### Bước 3: Deploy Web Service

1. Trong Render, click **"New +"** → **"Web Service"**
2. Connect GitHub repository của bạn
3. Cấu hình:

   - **Name**: `student-management`
   - **Region**: Singapore
   - **Branch**: `main`
   - **Runtime**: Docker
   - **Plan**: Free

4. **Environment Variables** (Thêm các biến sau):

```
DATABASE_URL=<paste-internal-database-url-từ-bước-2>
SECRET_KEY=<random-string-bất-kỳ-dài-32-ký-tự>
```

Ví dụ SECRET_KEY:

```
SECRET_KEY=abc123xyz789qwertyuiop4567890def
```

5. Click **"Create Web Service"**

### Bước 4: Khởi tạo Database

Sau khi deploy thành công:

1. Vào tab **"Shell"** của Web Service
2. Chạy lệnh khởi tạo database:

```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
...     print("Database created!")
>>> exit()
```

Hoặc tạo file `init_db.py`:

```python
from app import app, db, User

with app.app_context():
    db.create_all()

    # Tạo admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            role='admin',
            full_name='Administrator',
            email='admin@example.com'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
```

Chạy: `python init_db.py`

## Sử dụng

### Đăng nhập

Truy cập URL của ứng dụng và đăng nhập:

- **Admin**: username `admin`, password `admin123`

### Tạo thêm tài khoản

Bạn cần thêm code để tạo user mới hoặc dùng Shell:

```python
from app import app, db, User

with app.app_context():
    # Tạo giáo viên
    teacher = User(
        username='teacher1',
        role='teacher',
        full_name='Nguyễn Văn A',
        email='teacher@example.com'
    )
    teacher.set_password('teacher123')
    db.session.add(teacher)

    # Tạo sinh viên
    student = User(
        username='student1',
        role='student',
        full_name='Trần Thị B',
        email='student@example.com'
    )
    student.set_password('student123')
    db.session.add(student)

    db.session.commit()
    print("Users created!")
```

### Import sinh viên từ Excel

1. Chuẩn bị file Excel với các cột:

   - `student_id` (bắt buộc)
   - `full_name` (bắt buộc)
   - `email`, `phone`, `class_name`, `major` (tùy chọn)

2. Đăng nhập với tài khoản Admin
3. Vào menu **"Import Excel"**
4. Chọn file và upload

### Export danh sách

1. Vào menu **"Export Excel"**
2. File sẽ được tải về tự động

## Troubleshooting

### ⚠️ Lỗi Database Connection: "could not translate host name"

**Nguyên nhân**: DATABASE_URL không đúng hoặc thiếu domain đầy đủ

**Giải pháp nhanh**:

1. Vào Render PostgreSQL Dashboard
2. Copy **Internal Database URL** (KHÔNG phải External!)
3. Update Environment Variable `DATABASE_URL` trong Web Service
4. Format đúng phải là:

   ```
   postgresql://user:pass@dpg-xxxxx-a.region-postgres.render.com:5432/dbname
   ```

5. **Test connection** trước:
   ```bash
   export DATABASE_URL="your-database-url"
   python test_db.py
   ```

📖 **Chi tiết**: Xem file `TROUBLESHOOTING.md`

### Lỗi Database Connection (khác)

Kiểm tra:

- `DATABASE_URL` có đúng format không
- Database có status "Available" không (trên Render Dashboard)
- Web Service và Database cùng region không

### Lỗi 502 Bad Gateway

- Đợi vài phút để Render build xong
- Kiểm tra logs trong tab "Logs"
- Verify DATABASE_URL đã được set đúng

### Lỗi Permission Denied

- Đảm bảo role của user đúng (admin/teacher/student)

### Application không start được

1. Check logs: Tab "Logs" trong Render
2. Verify environment variables đã set đầy đủ
3. Test database connection với `test_db.py`
4. Thử "Clear build cache & deploy"

## Bảo mật

⚠️ **Lưu ý quan trọng:**

1. **Đổi mật khẩu admin ngay sau khi deploy**
2. Sử dụng `SECRET_KEY` mạnh và bảo mật
3. Không commit file `.env` lên Git
4. Sử dụng HTTPS trong production

## Nâng cấp

### Thêm tính năng gửi email

Cài thêm:

```bash
pip install Flask-Mail
```

### Thêm validation mạnh hơn

Cài thêm:

```bash
pip install Flask-WTF WTForms
```

### Thêm API

Cài thêm:

```bash
pip install Flask-RESTful
```

## License

MIT License - Tự do sử dụng cho mục đích học tập

## Liên hệ

Nếu có vấn đề, tạo issue trên GitHub hoặc liên hệ qua email.
