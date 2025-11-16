#!/usr/bin/env python
"""
Script khởi tạo database và tạo dữ liệu mẫu
Chạy: python init_db.py
"""

from app import app, db, User, Student, Subject, Score
from datetime import datetime

def init_database():
    """Khởi tạo database và tạo dữ liệu mẫu"""
    with app.app_context():
        print("Đang tạo database...")
        db.create_all()
        print("✓ Database đã được tạo")
        
        # Tạo admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                role='admin',
                full_name='Quản trị viên',
                email='admin@example.com'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✓ Tạo tài khoản admin")
        
        # Tạo giáo viên
        teacher = User.query.filter_by(username='teacher').first()
        if not teacher:
            teacher = User(
                username='teacher',
                role='teacher',
                full_name='Nguyễn Văn Giáo',
                email='teacher@example.com'
            )
            teacher.set_password('teacher123')
            db.session.add(teacher)
            print("✓ Tạo tài khoản giáo viên")
        
        # Tạo sinh viên
        student_user = User.query.filter_by(username='student').first()
        if not student_user:
            student_user = User(
                username='student',
                role='student',
                full_name='Trần Thị Sinh Viên',
                email='student@example.com'
            )
            student_user.set_password('student123')
            db.session.add(student_user)
            print("✓ Tạo tài khoản sinh viên")
        
        db.session.commit()
        
        # Tạo dữ liệu mẫu sinh viên
        if Student.query.count() == 0:
            students_data = [
                {
                    'student_id': 'SV001',
                    'full_name': 'Nguyễn Văn An',
                    'email': 'nva@student.edu.vn',
                    'phone': '0901234567',
                    'class_name': 'CNTT-K17',
                    'major': 'Công nghệ thông tin'
                },
                {
                    'student_id': 'SV002',
                    'full_name': 'Trần Thị Bình',
                    'email': 'ttb@student.edu.vn',
                    'phone': '0907654321',
                    'class_name': 'CNTT-K17',
                    'major': 'Công nghệ thông tin'
                },
                {
                    'student_id': 'SV003',
                    'full_name': 'Lê Văn Cường',
                    'email': 'lvc@student.edu.vn',
                    'phone': '0912345678',
                    'class_name': 'CNTT-K17',
                    'major': 'Khoa học máy tính'
                },
                {
                    'student_id': 'SV004',
                    'full_name': 'Phạm Thị Dung',
                    'email': 'ptd@student.edu.vn',
                    'phone': '0987654321',
                    'class_name': 'KTPM-K17',
                    'major': 'Kỹ thuật phần mềm'
                },
                {
                    'student_id': 'SV005',
                    'full_name': 'Hoàng Văn Em',
                    'email': 'hve@student.edu.vn',
                    'phone': '0923456789',
                    'class_name': 'KTPM-K17',
                    'major': 'Kỹ thuật phần mềm'
                }
            ]
            
            for data in students_data:
                student = Student(**data, status='active')
                db.session.add(student)
            
            print(f"✓ Tạo {len(students_data)} sinh viên mẫu")
        
        # Tạo môn học mẫu
        if Subject.query.count() == 0:
            subjects_data = [
                {
                    'subject_code': 'IT001',
                    'subject_name': 'Lập trình căn bản',
                    'credits': 3,
                    'semester': 'HK1-2024'
                },
                {
                    'subject_code': 'IT002',
                    'subject_name': 'Cấu trúc dữ liệu và giải thuật',
                    'credits': 4,
                    'semester': 'HK1-2024'
                },
                {
                    'subject_code': 'IT003',
                    'subject_name': 'Cơ sở dữ liệu',
                    'credits': 3,
                    'semester': 'HK1-2024'
                },
                {
                    'subject_code': 'IT004',
                    'subject_name': 'Mạng máy tính',
                    'credits': 3,
                    'semester': 'HK2-2024'
                },
                {
                    'subject_code': 'IT005',
                    'subject_name': 'Công nghệ web',
                    'credits': 4,
                    'semester': 'HK2-2024'
                }
            ]
            
            for data in subjects_data:
                subject = Subject(**data)
                db.session.add(subject)
            
            print(f"✓ Tạo {len(subjects_data)} môn học mẫu")
        
        db.session.commit()
        
        # Tạo điểm mẫu
        if Score.query.count() == 0:
            students = Student.query.all()
            subjects = Subject.query.limit(3).all()  # Chỉ lấy 3 môn đầu
            
            import random
            score_count = 0
            
            for student in students:
                for subject in subjects:
                    midterm = round(random.uniform(5.0, 10.0), 1)
                    final = round(random.uniform(5.0, 10.0), 1)
                    
                    score = Score(
                        student_id=student.id,
                        subject_id=subject.id,
                        midterm_score=midterm,
                        final_score=final,
                        semester='HK1-2024'
                    )
                    score.calculate_average()
                    db.session.add(score)
                    score_count += 1
            
            db.session.commit()
            print(f"✓ Tạo {score_count} bản ghi điểm mẫu")
        
        print("\n" + "="*50)
        print("KHỞI TẠO HOÀN TẤT!")
        print("="*50)
        print("\nTài khoản đăng nhập:")
        print("-" * 50)
        print("Admin:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nGiáo viên:")
        print("  Username: teacher")
        print("  Password: teacher123")
        print("\nSinh viên:")
        print("  Username: student")
        print("  Password: student123")
        print("-" * 50)
        print("\nTruy cập: http://localhost:5000")
        print()

if __name__ == '__main__':
    init_database()