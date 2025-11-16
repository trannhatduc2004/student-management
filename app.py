from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pandas as pd
import io
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration with better error handling
database_url = os.environ.get('DATABASE_URL', 'sqlite:///students.db')

# Fix postgres:// to postgresql:// for SQLAlchemy
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

# For Render internal URLs, use postgresql+psycopg2://
if 'render.com' in database_url and not database_url.startswith('postgresql+psycopg2://'):
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {
        'connect_timeout': 10,
        'options': '-c statement_timeout=30000'
    }
}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, student
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    birth_date = db.Column(db.Date)
    class_name = db.Column(db.String(50))
    major = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scores = db.relationship('Score', backref='student', lazy=True, cascade='all, delete-orphan')

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String(20), unique=True, nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.String(20))
    scores = db.relationship('Score', backref='subject', lazy=True, cascade='all, delete-orphan')

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    midterm_score = db.Column(db.Float)
    final_score = db.Column(db.Float)
    average_score = db.Column(db.Float)
    letter_grade = db.Column(db.String(2))
    semester = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_average(self):
        if self.midterm_score is not None and self.final_score is not None:
            self.average_score = round(self.midterm_score * 0.4 + self.final_score * 0.6, 2)
            self.letter_grade = self.get_letter_grade(self.average_score)
    
    @staticmethod
    def get_letter_grade(score):
        if score >= 9.0: return 'A+'
        elif score >= 8.5: return 'A'
        elif score >= 8.0: return 'B+'
        elif score >= 7.0: return 'B'
        elif score >= 6.5: return 'C+'
        elif score >= 5.5: return 'C'
        elif score >= 5.0: return 'D+'
        elif score >= 4.0: return 'D'
        else: return 'F'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Bạn cần quyền admin để truy cập trang này', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'teacher']:
            flash('Bạn cần quyền giáo viên để truy cập trang này', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất', 'info')
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    total_subjects = Subject.query.count()
    total_scores = Score.query.count()
    
    # Statistics
    active_students = Student.query.filter_by(status='active').count()
    
    # Recent students
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html', 
                         total_students=total_students,
                         total_subjects=total_subjects,
                         total_scores=total_scores,
                         active_students=active_students,
                         recent_students=recent_students)

@app.route('/teacher/dashboard')
@teacher_required
def teacher_dashboard():
    total_students = Student.query.count()
    total_subjects = Subject.query.count()
    recent_scores = Score.query.order_by(Score.created_at.desc()).limit(10).all()
    
    return render_template('teacher_dashboard.html',
                         total_students=total_students,
                         total_subjects=total_subjects,
                         recent_scores=recent_scores)

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    # In a real app, link User to Student
    student = Student.query.first()  # Simplified
    if student:
        scores = Score.query.filter_by(student_id=student.id).all()
        gpa = calculate_gpa(scores)
        return render_template('student_dashboard.html', student=student, scores=scores, gpa=gpa)
    return render_template('student_dashboard.html', student=None, scores=[], gpa=0)

# Student Management
@app.route('/students')
@teacher_required
def list_students():
    search = request.args.get('search', '')
    if search:
        students = Student.query.filter(
            (Student.student_id.contains(search)) | 
            (Student.full_name.contains(search))
        ).all()
    else:
        students = Student.query.all()
    return render_template('students.html', students=students, search=search)

@app.route('/students/add', methods=['GET', 'POST'])
@teacher_required
def add_student():
    if request.method == 'POST':
        student = Student(
            student_id=request.form['student_id'],
            full_name=request.form['full_name'],
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            class_name=request.form.get('class_name'),
            major=request.form.get('major'),
            status='active'
        )
        db.session.add(student)
        db.session.commit()
        flash('Thêm sinh viên thành công!', 'success')
        return redirect(url_for('list_students'))
    return render_template('add_student.html')

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@teacher_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.full_name = request.form['full_name']
        student.email = request.form.get('email')
        student.phone = request.form.get('phone')
        student.class_name = request.form.get('class_name')
        student.major = request.form.get('major')
        student.status = request.form.get('status')
        db.session.commit()
        flash('Cập nhật thông tin thành công!', 'success')
        return redirect(url_for('list_students'))
    return render_template('edit_student.html', student=student)

@app.route('/students/delete/<int:id>')
@admin_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Đã xóa sinh viên', 'success')
    return redirect(url_for('list_students'))

# Subject Management
@app.route('/subjects')
@teacher_required
def list_subjects():
    subjects = Subject.query.all()
    return render_template('subjects.html', subjects=subjects)

@app.route('/subjects/add', methods=['GET', 'POST'])
@teacher_required
def add_subject():
    if request.method == 'POST':
        subject = Subject(
            subject_code=request.form['subject_code'],
            subject_name=request.form['subject_name'],
            credits=int(request.form['credits']),
            semester=request.form.get('semester')
        )
        db.session.add(subject)
        db.session.commit()
        flash('Thêm môn học thành công!', 'success')
        return redirect(url_for('list_subjects'))
    return render_template('add_subject.html')

# Score Management
@app.route('/scores')
@teacher_required
def list_scores():
    scores = Score.query.all()
    return render_template('scores.html', scores=scores)

@app.route('/scores/add', methods=['GET', 'POST'])
@teacher_required
def add_score():
    if request.method == 'POST':
        score = Score(
            student_id=int(request.form['student_id']),
            subject_id=int(request.form['subject_id']),
            midterm_score=float(request.form['midterm_score']),
            final_score=float(request.form['final_score']),
            semester=request.form.get('semester')
        )
        score.calculate_average()
        db.session.add(score)
        db.session.commit()
        flash('Thêm điểm thành công!', 'success')
        return redirect(url_for('list_scores'))
    
    students = Student.query.all()
    subjects = Subject.query.all()
    return render_template('add_score.html', students=students, subjects=subjects)

# Import/Export
@app.route('/import/students', methods=['GET', 'POST'])
@admin_required
def import_students():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith(('.xlsx', '.xls')):
            try:
                df = pd.read_excel(file)
                required_columns = ['student_id', 'full_name']
                
                if not all(col in df.columns for col in required_columns):
                    flash('File Excel thiếu cột bắt buộc: student_id, full_name', 'danger')
                    return redirect(url_for('import_students'))
                
                count = 0
                for _, row in df.iterrows():
                    existing = Student.query.filter_by(student_id=str(row['student_id'])).first()
                    if not existing:
                        student = Student(
                            student_id=str(row['student_id']),
                            full_name=str(row['full_name']),
                            email=str(row.get('email', '')),
                            phone=str(row.get('phone', '')),
                            class_name=str(row.get('class_name', '')),
                            major=str(row.get('major', '')),
                            status='active'
                        )
                        db.session.add(student)
                        count += 1
                
                db.session.commit()
                flash(f'Import thành công {count} sinh viên!', 'success')
                return redirect(url_for('list_students'))
            except Exception as e:
                flash(f'Lỗi import: {str(e)}', 'danger')
        else:
            flash('Vui lòng chọn file Excel (.xlsx hoặc .xls)', 'danger')
    
    return render_template('import_students.html')

@app.route('/export/students')
@teacher_required
def export_students():
    students = Student.query.all()
    data = [{
        'Mã SV': s.student_id,
        'Họ tên': s.full_name,
        'Email': s.email,
        'Điện thoại': s.phone,
        'Lớp': s.class_name,
        'Chuyên ngành': s.major,
        'Trạng thái': s.status
    } for s in students]
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sinh viên')
    output.seek(0)
    
    return send_file(output, 
                     download_name='danh_sach_sinh_vien.xlsx',
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# API for charts
@app.route('/api/statistics')
@login_required
def api_statistics():
    # Grade distribution
    scores = Score.query.all()
    grade_counts = {}
    for score in scores:
        grade = score.letter_grade or 'N/A'
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    return jsonify({
        'grade_distribution': grade_counts,
        'total_students': Student.query.count(),
        'total_subjects': Subject.query.count(),
        'total_scores': len(scores)
    })

def calculate_gpa(scores):
    if not scores:
        return 0.0
    
    grade_points = {
        'A+': 4.0, 'A': 3.7, 'B+': 3.5, 'B': 3.0,
        'C+': 2.5, 'C': 2.0, 'D+': 1.5, 'D': 1.0, 'F': 0.0
    }
    
    total_points = 0
    total_credits = 0
    
    for score in scores:
        if score.letter_grade and score.subject:
            points = grade_points.get(score.letter_grade, 0)
            credits = score.subject.credits
            total_points += points * credits
            total_credits += credits
    
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

# Initialize database and create admin user
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
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
            print("Admin user created: username='admin', password='admin123'")

# Tự động khởi tạo DB khi app khởi động (cho Render)
def ensure_db_initialized():
    """Đảm bảo database đã được khởi tạo"""
    try:
        with app.app_context():
            # Tạo tất cả các bảng nếu chưa có
            db.create_all()
            
            # Tạo admin user nếu chưa có
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
                print("✓ Admin user created: username='admin', password='admin123'")
            else:
                print("✓ Admin user already exists")
                
    except Exception as e:
        # Log lỗi nhưng không crash app
        print(f"⚠️ DB initialization: {e}")

# Gọi hàm khởi tạo DB
ensure_db_initialized()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)