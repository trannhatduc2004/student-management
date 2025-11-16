# Quick Start Guide - 5 phút Deploy lên Render

## 📋 Checklist Cần Có

- [ ] Tài khoản GitHub
- [ ] Tài khoản Render (free)
- [ ] Code đã push lên GitHub

## 🚀 Deploy trong 5 bước

### Bước 1: Push Code lên GitHub (2 phút)

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/student-management.git
git push -u origin main
```

### Bước 2: Tạo PostgreSQL Database (1 phút)

1. Đăng nhập [Render](https://render.com)
2. **New +** → **PostgreSQL**
3. Settings:
   - Name: `student-db`
   - Region: **Singapore** ⭐
4. **Create Database**
5. ⚠️ **Copy Internal Database URL** (cần ở bước 4)

### Bước 3: Tạo Web Service (1 phút)

1. **New +** → **Web Service**
2. Connect GitHub repository
3. Settings:
   - Name: `student-management`
   - Region: **Singapore** ⭐
   - Runtime: **Docker**
   - Plan: Free

### Bước 4: Set Environment Variables (30 giây)

Thêm 2 biến này:

```bash
DATABASE_URL=<paste-internal-database-url-từ-bước-2>
SECRET_KEY=abc123xyz789randomstring321xyz
```

**Tạo SECRET_KEY**: Dùng bất kỳ chuỗi random 32 ký tự

4. **Create Web Service** → Đợi build (5-10 phút)

### Bước 5: Khởi tạo Database (30 giây)

Sau khi deploy xong:

1. Tab **Shell** trong Web Service
2. Chạy:

```bash
python init_db.py
```

Xong! Truy cập URL được cung cấp.

## 🔐 Login

- Username: `admin`
- Password: `admin123`

**⚠️ Đổi password ngay!**

## ❌ Nếu Lỗi "could not translate host name"

Có 99% là DATABASE_URL sai!

### Fix nhanh:

1. Vào PostgreSQL Dashboard trên Render
2. Tìm section "Connections"
3. Copy **Internal Database URL** (dòng đầu tiên)
4. Vào Web Service → Environment
5. Edit `DATABASE_URL` → Paste URL mới
6. Save → Đợi redeploy

### Verify URL đúng:

✅ **Đúng** (có đầy đủ domain):

```
postgresql://user:pass@dpg-xxxxx-a.singapore-postgres.render.com:5432/dbname
```

❌ **Sai** (thiếu domain):

```
postgresql://user:pass@dpg-xxxxx-a:5432/dbname
```

### Test trước khi deploy:

```bash
export DATABASE_URL="your-url-here"
python test_db.py
```

## 🎯 Các tính năng chính

1. **Quản lý sinh viên**: Thêm/sửa/xóa/tìm kiếm
2. **Quản lý môn học**: CRUD môn học
3. **Nhập điểm**: Tự động tính điểm TB, GPA
4. **Import Excel**: Nhập hàng loạt sinh viên
5. **Export Excel**: Xuất danh sách
6. **Dashboard**: Thống kê với biểu đồ

## 📱 Demo Workflow

### Admin:

1. Login → Dashboard
2. Import sinh viên từ Excel
3. Thêm môn học
4. Phân công giáo viên

### Giáo viên:

1. Login → Dashboard
2. Xem danh sách sinh viên
3. Nhập điểm cho sinh viên
4. Export báo cáo

### Sinh viên:

1. Login → Dashboard
2. Xem điểm cá nhân
3. Xem GPA

## 🔧 Local Development

```bash
# Install
pip install -r requirements.txt

# Init DB
python init_db.py

# Run
python app.py

# Access
http://localhost:5000
```

## 📚 Tài liệu đầy đủ

- **README.md** - Tổng quan và installation
- **DEPLOY.md** - Hướng dẫn deploy chi tiết
- **TROUBLESHOOTING.md** - Fix lỗi thường gặp

## 💡 Tips

✅ **Nên làm**:

- Đổi password admin ngay
- Backup database thường xuyên
- Monitor logs
- Test trên local trước khi deploy

❌ **Không nên**:

- Commit `.env` file
- Dùng admin/admin123 ở production
- Để database public
- Push sensitive data lên Git

## 🆘 Cần Giúp?

1. Check **TROUBLESHOOTING.md**
2. Run `python test_db.py` để test connection
3. Xem logs trong Render Dashboard
4. Google error message
5. Tạo issue trên GitHub

## ⚡ Common Issues & Fixes

| Issue             | Solution                          |
| ----------------- | --------------------------------- |
| Can't connect DB  | Use Internal DB URL, not External |
| 502 Gateway       | Wait for build to complete        |
| Login failed      | Run `python init_db.py`           |
| Import không work | Check Excel columns               |
| Slow response     | Free tier sleep after 15min       |

## 🎉 Done!

App đang chạy tại: `https://your-app.onrender.com`

Enjoy! 🚀
