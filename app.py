import os
import traceback
from flask import Flask, render_template, url_for, flash, redirect, send_from_directory, session, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user, logout_user, login_user, LoginManager, UserMixin
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from flask_compress import Compress
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.utils import secure_filename
import secrets
import psycopg2

app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = "login"
app.config["SECRET_KEY"] = "aokjijrgiljiwght"

def database():
    db_link = "postgresql://lyxin:JsVsgW7AGF6SWqoCdwXseMCg9CKhEQzD@dpg-d3am2ii4d50c73deb4kg-a.oregon-postgres.render.com/lyxspace"
    db_link2 = "sqlite:///default.db"
    if db_link:
        try:
            engine = create_engine(db_link)
            engine.connect().close()
            print("Connected to Database.")
            return db_link
        except OperationalError as e:
            print("Failed to Connect to Database.", e)
    else:
        print("Using default SQLite database.")
        return db_link2

app.config["SQLALCHEMY_DATABASE_URI"] = database()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"
# File upload configuration
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Static files folder
STATIC_FOLDER = os.path.join(app.root_path, 'static')
app.config['STATIC_FOLDER'] = STATIC_FOLDER
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)
db = SQLAlchemy(app)
Compress(app)
#--------------------------------------------------------------------
def nairobi_time():
    return datetime.utcnow() + timedelta(hours=3)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.Integer, unique=True, nullable=True)
    username = db.Column(db.String(255), nullable=True)
    login_at = db.Column(db.DateTime, default=nairobi_time)
    allowed = db.Column(db.String(255), default="no", nullable=True)
    
    @property
    def is_allowed(self):
        return self.allowed.lower() == "yes"

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    upload_date = db.Column(db.DateTime, default=nairobi_time)
    description = db.Column(db.Text)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#--------------------------------------------------------------------
#--------------------------------------------------------------------
# Enrollment and Course Models
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    long_description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    level = db.Column(db.String(100))
    duration = db.Column(db.String(100))
    lessons = db.Column(db.Integer)
    projects = db.Column(db.Integer)
    category = db.Column(db.String(100))
    color = db.Column(db.String(100))
    instructor = db.Column(db.String(255))
    rating = db.Column(db.Float, default=0.0)
    students = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0.0)
    resources = db.Column(db.Integer, default=0)
    quizzes = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=nairobi_time)

class CourseModule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    lessons = db.Column(db.Integer)
    duration = db.Column(db.String(100))
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=nairobi_time)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=nairobi_time)
    completed_at = db.Column(db.DateTime, nullable=True)
    progress = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship for easy access
    user = db.relationship('User', backref=db.backref('enrollments', lazy=True))
    course = db.relationship('Course', backref=db.backref('enrollments', lazy=True))
    
    # Unique constraint to prevent duplicate enrollments
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course'),)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('course_module.id'), nullable=False)
    lesson_id = db.Column(db.Integer)  # Could be linked to a Lesson model if you have one
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, default=0.0)  # For quizzes/exercises
    time_spent = db.Column(db.Integer, default=0)  # Time in seconds
    last_accessed = db.Column(db.DateTime, default=nairobi_time)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('progress', lazy=True))
    course = db.relationship('Course', backref=db.backref('progress', lazy=True))
    module = db.relationship('CourseModule', backref=db.backref('progress', lazy=True))
#--------------------------------------------------------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            flash("Admin access required.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def protect_file(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Login first to access.", "error")
            return redirect(url_for("login"))
        if not current_user.is_allowed:
            flash("Payment required to access files.", "warning")
            return redirect(url_for("files"))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#--------------------------------------------------------------------
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'favicon.ico')

# Serve uploaded files
@app.route('/uploads/<filename>')
@protect_file
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Serve static files
@app.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)

#--------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except OperationalError as e:
        print("Database connection lost", e)
        return None
#--------------------------------------------------------------------
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=732)
#--------------------------------------------------------------------
@app.route('/is_authenticated')
def is_authenticated():
    return jsonify({'authenticated': current_user.is_authenticated})
#--------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")
#--------------------------------------------------------------------
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Already logged in, redirect to main page
        return redirect(url_for('files'))
    next_page = request.args.get("next") or request.form.get("next")
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        username = request.form.get('username')
        # Check if user exists
        user = User.query.filter_by(mobile=mobile).first()
        if not user:
            # Create new user
            user = User(mobile=mobile, username=username, allowed="no")
            db.session.add(user)
            db.session.commit()
            flash("New account created. Please wait for admin approval.", "info")
        else:
            # Update username if provided
            if username and user.username != username:
                user.username = username
                db.session.commit()
        login_user(user)
        flash("Login successful!", "success")
        return redirect(next_page or url_for('files'))
    return render_template("login.html")

#--------------------------------------------------------------------
@app.route("/logout")
@login_required
def logout():
    # Delete user after logout (as requested)
    user_id = current_user.id
    logout_user()
    
    # Only delete if not admin
    if user_id != 1:
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
    
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

#--------------------------------------------------------------------
@app.route("/files")
@login_required
def files():
    files_list = []
    if current_user.is_allowed:
        files_list = File.query.order_by(File.upload_date.desc()).all()
    
    return render_template("files.html", files=files_list, user_allowed=current_user.is_allowed)

#--------------------------------------------------------------------
@app.route("/api/files")
@login_required
@protect_file
def api_files():
    files = File.query.order_by(File.upload_date.desc()).all()
    file_list = []
    for file in files:
        file_list.append({
            'id': file.id,
            'filename': file.filename,
            'filepath': file.filepath,
            'file_type': file.file_type,
            'upload_date': file.upload_date.isoformat(),
            'description': file.description
        })
    return jsonify(file_list)

#--------------------------------------------------------------------
@app.route("/api/upload", methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    description = request.form.get('description', '')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{base}_{timestamp}{ext}"
        ext = ext.lower()
        if ext == '.pdf':
            save_folder = app.config['STATIC_FOLDER']
            file_type = 'pdf'
        else:
            save_folder = app.config['UPLOAD_FOLDER']
            file_type = 'image'
        file.save(os.path.join(save_folder, unique_filename))
        # Store only the filename, not the full path
        new_file = File(
            filename=unique_filename,
            filepath=unique_filename,
            file_type=file_type,
            description=description,
            uploader_id=current_user.id
        )
        db.session.add(new_file)
        db.session.commit()
        return jsonify({'message': 'File uploaded successfully'}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

#--------------------------------------------------------------------
@app.route("/api/download/<int:file_id>", methods=['POST'])
@login_required
@protect_file
def download_file(file_id):
    security_answer = request.json.get('security_answer', '')
    
    # Security check
    if security_answer.lower() != 'lyxspace2025':
        return jsonify({'error': 'Security check failed'}), 403
    
    file_data = File.query.get_or_404(file_id)
    # Determine folder
    if file_data.file_type == 'pdf':
        folder = app.config['STATIC_FOLDER']
    else:
        folder = app.config['UPLOAD_FOLDER']
    return send_file(os.path.join(folder, file_data.filepath), as_attachment=True, download_name=file_data.filename)

#--------------------------------------------------------------------
@app.route("/api/file/<int:file_id>")
@login_required
@protect_file
def get_file(file_id):
    file_data = File.query.get_or_404(file_id)
    if file_data.file_type == 'pdf':
        folder = app.config['STATIC_FOLDER']
    else:
        folder = app.config['UPLOAD_FOLDER']
    return send_file(os.path.join(folder, file_data.filepath))
#--------------------------------------------------------------------
#--------------------------------------------------------------------
# Courses Route
@app.route("/courses")
@login_required
def courses():
    try:
        # Get all active courses from database
        courses_data = Course.query.filter_by(is_active=True).order_by(Course.created_at.desc()).all()
        
        # Convert to list of dictionaries for template
        courses_list = []
        for course in courses_data:
            # Get enrollment count for this course
            enrollment_count = Enrollment.query.filter_by(course_id=course.id, is_active=True).count()
            
            courses_list.append({
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'icon': course.icon,
                'level': course.level,
                'duration': course.duration,
                'lessons': int(course.lessons) if course.lessons is not None else 0,
                'category': course.category,
                'color': course.color,
                'badge': 'Popular' if enrollment_count > 100 else 'New',
                'enrollment_count': enrollment_count,
                'is_enrolled': Enrollment.query.filter_by(
                    user_id=current_user.id, 
                    course_id=course.id, 
                    is_active=True
                ).first() is not None
            })
        
        categories = list(set([course['category'] for course in courses_list]))
        
        return render_template("courses.html", courses=courses_list, categories=categories)
        
    except Exception as e:
        flash("Error loading courses. Please try again.", "error")
        print(f"Error in courses route: {e}")
        return render_template("courses.html", courses=[], categories=[])

#--------------------------------------------------------------------
# Course Detail Route
@app.route("/course/<int:course_id>")
@login_required
def course_detail(course_id):
    try:
        # Get course from database
        course = Course.query.filter_by(id=course_id, is_active=True).first_or_404()
        
        # Get modules for this course
        modules = CourseModule.query.filter_by(course_id=course_id).order_by(CourseModule.order).all()
        
        # Check if user is enrolled
        enrollment = Enrollment.query.filter_by(
            user_id=current_user.id, 
            course_id=course_id, 
            is_active=True
        ).first()
        
        # Get enrollment count
        enrollment_count = Enrollment.query.filter_by(course_id=course_id, is_active=True).count()
        
        # Convert to dictionary for template
        course_data = {
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'long_description': course.long_description,
            'icon': course.icon,
            'level': course.level,
            'duration': course.duration,
            'lessons': course.lessons,
            'projects': course.projects,
            'category': course.category,
            'color': course.color,
            'instructor': course.instructor,
            'rating': course.rating,
            'students': int(enrollment_count) if enrollment_count is not None else 0,
            'price': f"${course.price:.2f}" if course.price > 0 else "Free",

            # ✅ Use a new key name to avoid conflict with DB field
            'module_list': [
                {
                    'title': module.title,
                    'lessons': module.lessons,
                    'duration': module.duration,
                    'id': module.id
                } for module in modules
            ] if modules else [],

            # ✅ These are integers (counts), keep them as such
            'resources': course.resources or 0,
            'quizzes': course.quizzes or 0,

            # ✅ Enrollment details
            'is_enrolled': enrollment is not None,
            'progress': enrollment.progress if enrollment else 0.0
        }
        import pprint
        print("\n=== DEBUG: course_data ===")
        pprint.pprint(course_data)
        print("=== END DEBUG ===\n")

        return render_template("course_detail.html", course=course_data)

    except Exception as e:
        flash("Course not found or error loading course details.", "error")
        print(f"Error in course_detail route: {e}")
        traceback.print_exc()
        return redirect(url_for('courses'))

#--------------------------------------------------------------------
# Enroll in Course Route
@app.route("/course/<int:course_id>/enroll", methods=['POST'])
@login_required
def enroll_course(course_id):
    try:
        # Check if course exists and is active
        course = Course.query.filter_by(id=course_id, is_active=True).first()
        if not course:
            flash("Course not found or no longer available.", "error")
            return redirect(url_for('courses'))
        
        # Check if user is already enrolled
        existing_enrollment = Enrollment.query.filter_by(
            user_id=current_user.id, 
            course_id=course_id
        ).first()
        
        if existing_enrollment:
            if existing_enrollment.is_active:
                flash(f"You are already enrolled in '{course.title}'.", "info")
            else:
                # Reactivate existing enrollment
                existing_enrollment.is_active = True
                existing_enrollment.enrolled_at = nairobi_time()
                db.session.commit()
                flash(f"Welcome back to '{course.title}'! Your enrollment has been reactivated.", "success")
        else:
            # Create new enrollment
            enrollment = Enrollment(
                user_id=current_user.id,
                course_id=course_id,
                enrolled_at=nairobi_time(),
                progress=0.0,
                is_active=True
            )
            db.session.add(enrollment)
            db.session.commit()
            flash(f"Successfully enrolled in '{course.title}'! Start your learning journey now.", "success")
        
        return redirect(url_for('course_detail', course_id=course_id))
        
    except Exception as e:
        db.session.rollback()
        flash("Error enrolling in course. Please try again.", "error")
        print(f"Error in enroll_course route: {e}")
        return redirect(url_for('course_detail', course_id=course_id))

#--------------------------------------------------------------------
# Unenroll from Course Route
@app.route("/course/<int:course_id>/unenroll", methods=['POST'])
@login_required
def unenroll_course(course_id):
    try:
        enrollment = Enrollment.query.filter_by(
            user_id=current_user.id, 
            course_id=course_id,
            is_active=True
        ).first()
        
        if enrollment:
            enrollment.is_active = False
            db.session.commit()
            flash("You have been unenrolled from the course.", "info")
        else:
            flash("You are not enrolled in this course.", "warning")
        
        return redirect(url_for('courses'))
        
    except Exception as e:
        db.session.rollback()
        flash("Error unenrolling from course. Please try again.", "error")
        print(f"Error in unenroll_course route: {e}")
        return redirect(url_for('course_detail', course_id=course_id))

#--------------------------------------------------------------------
# My Courses Route - Dashboard for enrolled courses
@app.route("/my-courses")
@login_required
def my_courses():
    try:
        # Get user's active enrollments with course details
        enrollments = Enrollment.query.filter_by(
            user_id=current_user.id, 
            is_active=True
        ).join(Course).order_by(Enrollment.enrolled_at.desc()).all()

        # Build a list of course dicts for the template
        courses_list = []
        for enrollment in enrollments:
            course = enrollment.course
            courses_list.append({
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'icon': course.icon,
                'level': course.level,
                'duration': course.duration,
                'lessons': course.lessons,
                'category': course.category,
                'color': course.color,
                'badge': 'Popular' if Enrollment.query.filter_by(course_id=course.id, is_active=True).count() > 100 else 'New',
                'enrollment_count': Enrollment.query.filter_by(course_id=course.id, is_active=True).count(),
                'is_enrolled': True,
                'progress': enrollment.progress,
                'enrolled_at': enrollment.enrolled_at
            })

        return render_template("my_courses.html", courses=courses_list)

    except Exception as e:
        flash("Error loading your courses. Please try again.", "error")
        print(f"Error in my_courses route: {e}")
        return render_template("my_courses.html", courses=[])

#--------------------------------------------------------------------
# Update Progress Route (AJAX)
@app.route("/api/course/<int:course_id>/progress", methods=['POST'])
@login_required
def update_progress(course_id):
    try:
        data = request.get_json()
        lesson_id = data.get('lesson_id')
        module_id = data.get('module_id')
        completed = data.get('completed', False)
        score = data.get('score', 0.0)
        time_spent = data.get('time_spent', 0)
        
        # Check if user is enrolled
        enrollment = Enrollment.query.filter_by(
            user_id=current_user.id, 
            course_id=course_id,
            is_active=True
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled in this course'}), 403
        
        # Update or create progress record
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            course_id=course_id,
            module_id=module_id,
            lesson_id=lesson_id
        ).first()
        
        if progress:
            progress.completed = completed
            progress.score = max(progress.score, score)  # Keep highest score
            progress.time_spent += time_spent
            progress.last_accessed = nairobi_time()
            if completed and not progress.completed_at:
                progress.completed_at = nairobi_time()
        else:
            progress = UserProgress(
                user_id=current_user.id,
                course_id=course_id,
                module_id=module_id,
                lesson_id=lesson_id,
                completed=completed,
                score=score,
                time_spent=time_spent,
                last_accessed=nairobi_time()
            )
            if completed:
                progress.completed_at = nairobi_time()
            db.session.add(progress)
        
        # Update overall course progress
        total_lessons = CourseModule.query.filter_by(course_id=course_id).with_entities(
            db.func.sum(CourseModule.lessons)
        ).scalar() or 0
        
        if total_lessons > 0:
            completed_lessons = UserProgress.query.filter_by(
                user_id=current_user.id,
                course_id=course_id,
                completed=True
            ).count()
            
            enrollment.progress = min(completed_lessons / total_lessons, 1.0)
            
            # Mark as completed if progress is 100%
            if enrollment.progress >= 1.0 and not enrollment.completed_at:
                enrollment.completed_at = nairobi_time()
                # You could trigger a certificate generation here
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'progress': enrollment.progress,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_progress route: {e}")
        return jsonify({'error': 'Failed to update progress'}), 500

#--------------------------------------------------------------------
#--------------------------------------------------------------------
# Admin Route to Add Comprehensive Sample Courses
@app.route("/admin/seed-courses")
@login_required
@admin_required
def seed_courses():
    try:
        # Comprehensive sample courses data
        sample_courses = [
            # Ubuntu & Linux Courses
            {
                'title': 'Ubuntu & Linux Mastery',
                'description': 'Complete guide to Linux command line, system administration, and shell scripting',
                'long_description': 'This comprehensive course takes you from Linux beginner to proficient system administrator. You\'ll learn essential command line skills, file system management, user administration, networking, security, and automation with shell scripting. Perfect for aspiring DevOps engineers and system administrators.',
                'icon': 'fa-terminal',
                'level': 'Beginner to Advanced',
                'duration': '6 weeks',
                'lessons': 24,
                'projects': 5,
                'category': 'System Administration',
                'color': 'from-green-500 to-emerald-600',
                'instructor': 'Mr. Vincent',
                'rating': 4.8,
                'price': 49.99,
                'resources': 15,
                'quizzes': 6,
                'modules': [
                    {'title': 'Linux Fundamentals & Installation', 'lessons': 4, 'duration': '1 week', 'order': 1},
                    {'title': 'Command Line Mastery', 'lessons': 5, 'duration': '1.5 weeks', 'order': 2},
                    {'title': 'File System & Permissions', 'lessons': 4, 'duration': '1 week', 'order': 3},
                    {'title': 'User & Process Management', 'lessons': 3, 'duration': '1 week', 'order': 4},
                    {'title': 'Networking & Security', 'lessons': 4, 'duration': '1 week', 'order': 5},
                    {'title': 'Shell Scripting & Automation', 'lessons': 4, 'duration': '1.5 weeks', 'order': 6}
                ]
            },
            {
                'title': 'Linux Server Administration',
                'description': 'Advanced Linux server management, security, and deployment strategies',
                'long_description': 'Master enterprise-level Linux server administration with this advanced course. Learn about system services, security hardening, performance tuning, containerization, and enterprise deployment strategies. Essential for DevOps professionals and system architects.',
                'icon': 'fa-server',
                'level': 'Advanced',
                'duration': '5 weeks',
                'lessons': 20,
                'projects': 4,
                'category': 'System Administration',
                'color': 'from-purple-500 to-pink-500',
                'instructor': 'Mr. Lyxin',
                'rating': 4.8,
                'price': 79.99,
                'resources': 18,
                'quizzes': 5,
                'modules': [
                    {'title': 'Server Setup & Configuration', 'lessons': 4, 'duration': '1 week', 'order': 1},
                    {'title': 'Service Management (Systemd)', 'lessons': 4, 'duration': '1 week', 'order': 2},
                    {'title': 'Security Hardening & Firewalls', 'lessons': 4, 'duration': '1 week', 'order': 3},
                    {'title': 'Performance Monitoring & Tuning', 'lessons': 3, 'duration': '1 week', 'order': 4},
                    {'title': 'Containerization with Docker', 'lessons': 3, 'duration': '1 week', 'order': 5},
                    {'title': 'Enterprise Deployment Strategies', 'lessons': 2, 'duration': '1 week', 'order': 6}
                ]
            },
            {
                'title': 'Bash Shell Scripting Mastery',
                'description': 'Automate tasks and master shell scripting for system administration',
                'long_description': 'Learn to write powerful bash scripts to automate repetitive tasks, manage systems, and create efficient workflows. From basic scripts to advanced automation techniques, this course will make you a shell scripting expert.',
                'icon': 'fa-code',
                'level': 'Intermediate',
                'duration': '4 weeks',
                'lessons': 16,
                'projects': 3,
                'category': 'System Administration',
                'color': 'from-blue-500 to-cyan-500',
                'instructor': 'Ms. Marion',
                'rating': 4.6,
                'price': 39.99,
                'resources': 12,
                'quizzes': 4,
                'modules': [
                    {'title': 'Bash Fundamentals', 'lessons': 3, 'duration': '1 week', 'order': 1},
                    {'title': 'Variables & Control Structures', 'lessons': 4, 'duration': '1 week', 'order': 2},
                    {'title': 'Functions & Advanced Scripting', 'lessons': 4, 'duration': '1 week', 'order': 3},
                    {'title': 'System Automation & Scheduling', 'lessons': 3, 'duration': '1 week', 'order': 4},
                    {'title': 'Real-world Scripting Projects', 'lessons': 2, 'duration': '1 week', 'order': 5}
                ]
            },

            # HTML & CSS Courses
            {
                'title': 'HTML5 & CSS3 Fundamentals',
                'description': 'Build modern, responsive websites with latest HTML5 and CSS3 features',
                'long_description': 'Start your web development journey with this comprehensive HTML5 and CSS3 course. Learn semantic HTML, CSS layouts, responsive design, animations, and modern web development practices. Perfect for beginners starting their frontend development career.',
                'icon': 'fa-html5',
                'level': 'Beginner',
                'duration': '4 weeks',
                'lessons': 18,
                'projects': 4,
                'category': 'Web Development',
                'color': 'from-orange-500 to-red-500',
                'instructor': 'Mr. Vincent',
                'rating': 4.6,
                'price': 39.99,
                'resources': 12,
                'quizzes': 4,
                'modules': [
                    {'title': 'HTML5 Basics & Semantic Elements', 'lessons': 4, 'duration': '1 week', 'order': 1},
                    {'title': 'CSS3 Fundamentals & Styling', 'lessons': 5, 'duration': '1 week', 'order': 2},
                    {'title': 'Layouts & Positioning Techniques', 'lessons': 4, 'duration': '1 week', 'order': 3},
                    {'title': 'Responsive Design & Media Queries', 'lessons': 3, 'duration': '1 week', 'order': 4},
                    {'title': 'Advanced CSS Features & Animations', 'lessons': 2, 'duration': '1 week', 'order': 5}
                ]
            },
            {
                'title': 'Responsive Web Design',
                'description': 'Create mobile-first, responsive designs with CSS Grid, Flexbox, and frameworks',
                'long_description': 'Learn to create beautiful, responsive websites that work perfectly on all devices. Master CSS Grid, Flexbox, media queries, and modern design frameworks to build professional-grade web interfaces that adapt to any screen size.',
                'icon': 'fa-laptop-code',
                'level': 'Intermediate',
                'duration': '3 weeks',
                'lessons': 12,
                'projects': 3,
                'category': 'Web Development',
                'color': 'from-pink-500 to-rose-500',
                'instructor': 'Mr. Lyxin',
                'rating': 4.5,
                'price': 34.99,
                'resources': 10,
                'quizzes': 3,
                'modules': [
                    {'title': 'CSS Grid Mastery', 'lessons': 3, 'duration': '1 week', 'order': 1},
                    {'title': 'Flexbox Techniques & Layouts', 'lessons': 3, 'duration': '1 week', 'order': 2},
                    {'title': 'Responsive Frameworks (Bootstrap)', 'lessons': 3, 'duration': '1 week', 'order': 3},
                    {'title': 'Advanced Responsive Patterns', 'lessons': 3, 'duration': '1 week', 'order': 4}
                ]
            },
            {
                'title': 'Advanced CSS & Sass',
                'description': 'Master advanced CSS techniques, preprocessors, and modern workflow',
                'long_description': 'Take your CSS skills to the next level with advanced techniques, Sass preprocessor, CSS architecture, and modern development workflows. Learn to write maintainable, scalable CSS for large projects.',
                'icon': 'fa-sass',
                'level': 'Advanced',
                'duration': '4 weeks',
                'lessons': 16,
                'projects': 3,
                'category': 'Web Development',
                'color': 'from-purple-500 to-indigo-500',
                'instructor': 'Mr. Lyxin',
                'rating': 4.7,
                'price': 49.99,
                'resources': 14,
                'quizzes': 4,
                'modules': [
                    {'title': 'Sass Fundamentals & Mixins', 'lessons': 4, 'duration': '1 week', 'order': 1},
                    {'title': 'CSS Architecture & Methodologies', 'lessons': 4, 'duration': '1 week', 'order': 2},
                    {'title': 'Advanced Animations & Transitions', 'lessons': 4, 'duration': '1 week', 'order': 3},
                    {'title': 'Performance Optimization', 'lessons': 4, 'duration': '1 week', 'order': 4}
                ]
            },

            # JavaScript Courses
            {
                'title': 'JavaScript Programming',
                'description': 'Master JavaScript from basics to advanced concepts and modern frameworks',
                'long_description': 'Dive deep into JavaScript programming with this comprehensive course. Learn everything from basic syntax to advanced concepts like closures, promises, async/await, and modern frameworks. Become a proficient JavaScript developer ready for real-world projects.',
                'icon': 'fa-js-square',
                'level': 'Intermediate',
                'duration': '8 weeks',
                'lessons': 32,
                'projects': 6,
                'category': 'Web Development',
                'color': 'from-yellow-500 to-amber-600',
                'instructor': 'Mr. Lyxin',
                'rating': 4.7,
                'price': 59.99,
                'resources': 20,
                'quizzes': 8,
                'modules': [
                    {'title': 'JavaScript Basics & Fundamentals', 'lessons': 6, 'duration': '1.5 weeks', 'order': 1},
                    {'title': 'DOM Manipulation & Events', 'lessons': 5, 'duration': '1.5 weeks', 'order': 2},
                    {'title': 'Advanced JavaScript Concepts', 'lessons': 6, 'duration': '2 weeks', 'order': 3},
                    {'title': 'Async Programming & APIs', 'lessons': 4, 'duration': '1 week', 'order': 4},
                    {'title': 'Modern Frameworks Overview', 'lessons': 5, 'duration': '1.5 weeks', 'order': 5},
                    {'title': 'Project Development & Best Practices', 'lessons': 6, 'duration': '1.5 weeks', 'order': 6}
                ]
            },
            {
                'title': 'React.js Development',
                'description': 'Build modern web applications with React.js and ecosystem',
                'long_description': 'Learn to build scalable, maintainable web applications using React.js. Master components, hooks, state management, routing, and the entire React ecosystem including Redux, Context API, and modern testing practices.',
                'icon': 'fa-react',
                'level': 'Intermediate',
                'duration': '6 weeks',
                'lessons': 24,
                'projects': 4,
                'category': 'Web Development',
                'color': 'from-blue-400 to-cyan-400',
                'instructor': 'Mr. Lyxin',
                'rating': 4.8,
                'price': 69.99,
                'resources': 18,
                'quizzes': 6,
                'modules': [
                    {'title': 'React Fundamentals & JSX', 'lessons': 4, 'duration': '1 week', 'order': 1},
                    {'title': 'Components & Props', 'lessons': 4, 'duration': '1 week', 'order': 2},
                    {'title': 'State Management & Hooks', 'lessons': 5, 'duration': '1.5 weeks', 'order': 3},
                    {'title': 'Routing & API Integration', 'lessons': 4, 'duration': '1 week', 'order': 4},
                    {'title': 'Advanced Patterns & Performance', 'lessons': 4, 'duration': '1 week', 'order': 5},
                    {'title': 'Testing & Deployment', 'lessons': 3, 'duration': '1.5 weeks', 'order': 6}
                ]
            },
            {
                'title': 'Node.js Backend Development',
                'description': 'Build scalable server-side applications with Node.js and Express',
                'long_description': 'Master backend development with Node.js. Learn to build RESTful APIs, work with databases, implement authentication, and deploy production-ready applications. Essential for full-stack developers.',
                'icon': 'fa-node-js',
                'level': 'Intermediate',
                'duration': '5 weeks',
                'lessons': 20,
                'projects': 4,
                'category': 'Web Development',
                'color': 'from-green-500 to-green-700',
                'instructor': 'Mr. Lyxin',
                'rating': 4.6,
                'price': 59.99,
                'resources': 16,
                'quizzes': 5,
                'modules': [
                    {'title': 'Node.js Fundamentals', 'lessons': 4, 'duration': '1 week', 'order': 1},
                    {'title': 'Express.js & Middleware', 'lessons': 4, 'duration': '1 week', 'order': 2},
                    {'title': 'Database Integration', 'lessons': 4, 'duration': '1 week', 'order': 3},
                    {'title': 'Authentication & Security', 'lessons': 4, 'duration': '1 week', 'order': 4},
                    {'title': 'API Development & Deployment', 'lessons': 4, 'duration': '1 week', 'order': 5}
                ]
            },

            # Python Courses
            {
                'title': 'Python Development',
                'description': 'Learn Python programming, web development with Django/Flask, and data science',
                'long_description': 'Become a Python expert with this all-in-one course covering programming fundamentals, web development, data analysis, and automation. Perfect for beginners and those looking to advance their skills in one of the most versatile programming languages.',
                'icon': 'fa-python',
                'level': 'Beginner to Advanced',
                'duration': '10 weeks',
                'lessons': 40,
                'projects': 8,
                'category': 'Programming',
                'color': 'from-blue-500 to-cyan-500',
                'instructor': 'Mr. Lyxin',
                'rating': 4.9,
                'price': 69.99,
                'resources': 25,
                'quizzes': 10,
                'modules': [
                    {'title': 'Python Fundamentals', 'lessons': 8, 'duration': '2 weeks', 'order': 1},
                    {'title': 'Data Structures & Algorithms', 'lessons': 6, 'duration': '1.5 weeks', 'order': 2},
                    {'title': 'Web Development with Flask', 'lessons': 7, 'duration': '2 weeks', 'order': 3},
                    {'title': 'Data Science & Analysis', 'lessons': 6, 'duration': '1.5 weeks', 'order': 4},
                    {'title': 'Automation & Scripting', 'lessons': 5, 'duration': '1.5 weeks', 'order': 5},
                    {'title': 'Advanced Python Topics', 'lessons': 4, 'duration': '1 week', 'order': 6},
                    {'title': 'Capstone Project', 'lessons': 4, 'duration': '1.5 weeks', 'order': 7}
                ]
            },
            {
                'title': 'Flask Web Framework',
                'description': 'Build powerful web applications with Flask and Python',
                'long_description': 'Master the Flask web framework to build robust, scalable web applications. Learn about routing, templates, forms, authentication, and deployment. Perfect for Python developers wanting to build production-ready web applications.',
                'icon': 'fa-code',
                'level': 'Intermediate',
                'duration': '6 weeks',
                'lessons': 24,
                'projects': 4,
                'category': 'Programming',
                'color': 'from-green-600 to-green-800',
                'instructor': 'Mr. Vincent',
                'rating': 4.7,
                'price': 54.99,
                'resources': 18,
                'quizzes': 6,
                'modules': [
                    {'title': 'Django Fundamentals & Setup', 'lessons': 4, 'duration': '1 week', 'order': 1},
                    {'title': 'Models & Database Design', 'lessons': 5, 'duration': '1.5 weeks', 'order': 2},
                    {'title': 'Views & URL Routing', 'lessons': 4, 'duration': '1 week', 'order': 3},
                    {'title': 'Templates & Frontend Integration', 'lessons': 4, 'duration': '1 week', 'order': 4},
                    {'title': 'Forms & User Input', 'lessons': 3, 'duration': '1 week', 'order': 5},
                    {'title': 'Authentication & Deployment', 'lessons': 4, 'duration': '1.5 weeks', 'order': 6}
                ]
            },
            {
                'title': 'Python for Data Science',
                'description': 'Data analysis, visualization, and machine learning with Python',
                'long_description': 'Learn to analyze data, create visualizations, and build machine learning models using Python. Master libraries like Pandas, NumPy, Matplotlib, and Scikit-learn to extract insights from data and make data-driven decisions.',
                'icon': 'fa-chart-line',
                'level': 'Intermediate',
                'duration': '7 weeks',
                'lessons': 28,
                'projects': 5,
                'category': 'Data Science',
                'color': 'from-purple-500 to-pink-500',
                'instructor': 'Mr. Vincent',
                'rating': 4.8,
                'price': 64.99,
                'resources': 22,
                'quizzes': 7,
                'modules': [
                    {'title': 'Python for Data Analysis', 'lessons': 5, 'duration': '1.5 weeks', 'order': 1},
                    {'title': 'Pandas & Data Manipulation', 'lessons': 6, 'duration': '1.5 weeks', 'order': 2},
                    {'title': 'Data Visualization', 'lessons': 5, 'duration': '1.5 weeks', 'order': 3},
                    {'title': 'Statistical Analysis', 'lessons': 4, 'duration': '1 week', 'order': 4},
                    {'title': 'Machine Learning Fundamentals', 'lessons': 5, 'duration': '1.5 weeks', 'order': 5},
                    {'title': 'Real-world Data Projects', 'lessons': 3, 'duration': '1 week', 'order': 6}
                ]
            },
            {
                'title': 'Automation with Python',
                'description': 'Automate tasks and workflows using Python scripting',
                'long_description': 'Learn to automate repetitive tasks, file operations, web scraping, and system administration using Python. Save time and increase productivity with powerful automation scripts that handle boring tasks for you.',
                'icon': 'fa-robot',
                'level': 'Beginner to Intermediate',
                'duration': '4 weeks',
                'lessons': 16,
                'projects': 4,
                'category': 'Programming',
                'color': 'from-orange-500 to-red-500',
                'instructor': 'Mr. Lyxin',
                'rating': 4.5,
                'price': 44.99,
                'resources': 14,
                'quizzes': 4,
                'modules': [
                    {'title': 'Python Scripting Basics', 'lessons': 4, 'duration': '1 week', 'order': 1},
                    {'title': 'File & System Automation', 'lessons': 4, 'duration': '1 week', 'order': 2},
                    {'title': 'Web Automation & Scraping', 'lessons': 4, 'duration': '1 week', 'order': 3},
                    {'title': 'API Automation & Integration', 'lessons': 4, 'duration': '1 week', 'order': 4}
                ]
            }
        ]

        courses_added = 0
        modules_added = 0

        for course_data in sample_courses:
            # Check if course already exists
            existing_course = Course.query.filter_by(title=course_data['title']).first()
            if not existing_course:
                # Extract modules before creating course
                modules = course_data.pop('modules', [])
                
                # Create course
                course = Course(**course_data)
                db.session.add(course)
                db.session.flush()  # To get the course ID
                courses_added += 1
                
                # Add modules for this course
                for module_data in modules:
                    module = CourseModule(course_id=course.id, **module_data)
                    db.session.add(module)
                    modules_added += 1
        
        db.session.commit()
        
        flash(f"Successfully added {courses_added} courses and {modules_added} modules to the database!", "success")
        
        # Log the action
        print(f"Admin {current_user.username} seeded {courses_added} courses with {modules_added} modules")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error seeding courses: {str(e)}", "error")
        print(f"Error in seed_courses route: {e}")
    
    return redirect(url_for('admin_panel'))

#--------------------------------------------------------------------
# Admin Route to Clear All Courses (Dangerous - for development only)
@app.route("/admin/clear-courses")
@login_required
@admin_required
def clear_courses():
    try:
        # Get counts before deletion
        course_count = Course.query.count()
        module_count = CourseModule.query.count()
        enrollment_count = Enrollment.query.count()
        progress_count = UserProgress.query.count()
        
        # Delete in correct order to maintain referential integrity
        UserProgress.query.delete()
        Enrollment.query.delete()
        CourseModule.query.delete()
        Course.query.delete()
        
        db.session.commit()
        
        flash(f"Cleared {course_count} courses, {module_count} modules, {enrollment_count} enrollments, and {progress_count} progress records.", "warning")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error clearing courses: {str(e)}", "error")
    
    return redirect(url_for('admin_panel'))

#--------------------------------------------------------------------
# Admin Route to View Course Statistics
@app.route("/admin/course-stats")
@login_required
@admin_required
def course_stats():
    try:
        stats = {
            'total_courses': Course.query.count(),
            'active_courses': Course.query.filter_by(is_active=True).count(),
            'total_modules': CourseModule.query.count(),
            'total_enrollments': Enrollment.query.count(),
            'active_enrollments': Enrollment.query.filter_by(is_active=True).count(),
            'completed_enrollments': Enrollment.query.filter(Enrollment.completed_at.isnot(None)).count(),
            'total_progress_records': UserProgress.query.count(),
            'courses_by_category': db.session.query(
                Course.category, 
                db.func.count(Course.id)
            ).group_by(Course.category).all(),
            'popular_courses': db.session.query(
                Course.title,
                db.func.count(Enrollment.id)
            ).join(Enrollment).group_by(Course.title).order_by(db.func.count(Enrollment.id).desc()).limit(5).all()
        }
        
        return render_template("admin_course_stats.html", stats=stats)
        
    except Exception as e:
        flash(f"Error loading course statistics: {str(e)}", "error")
        return redirect(url_for('admin_panel'))
#--------------------------------------------------------------------
@app.route("/admin")
@login_required
@admin_required
def admin_panel():
    users = User.query.filter(User.id != 1).all()  # Exclude admin
    files = File.query.all()
    return render_template("admin.html", users=users, files=files)

#--------------------------------------------------------------------
@app.route("/admin/allow_user/<int:user_id>", methods=['POST'])
@login_required
@admin_required
def allow_user(user_id):
    user = User.query.get_or_404(user_id)
    user.allowed = "yes"
    db.session.commit()
    flash(f"User {user.username or user.mobile} has been allowed access.", "success")
    return redirect(url_for('admin_panel'))

#--------------------------------------------------------------------
@app.route("/admin/revoke_user/<int:user_id>", methods=['POST'])
@login_required
@admin_required
def revoke_user(user_id):
    user = User.query.get_or_404(user_id)
    user.allowed = "no"
    db.session.commit()
    flash(f"User {user.username or user.mobile} access has been revoked.", "warning")
    return redirect(url_for('admin_panel'))

#--------------------------------------------------------------------
@app.route("/admin/delete_file/<int:file_id>", methods=['POST'])
@login_required
#@admin_required
def delete_file(file_id):
    file_data = File.query.get_or_404(file_id)
    
    # Delete physical file
    # Remove from correct folder
    if file_data.file_type == 'pdf':
        folder = app.config['STATIC_FOLDER']
    else:
        folder = app.config['UPLOAD_FOLDER']
    file_path = os.path.join(folder, file_data.filepath)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(file_data)
    db.session.commit()
    flash("File deleted successfully.", "success")
    return redirect(url_for('admin_panel'))

#--------------------------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Internal Server Error: {error}', exc_info=True)
    flash('Oops! Something went wrong. Try again.', 'error')

    # Fallback to home if referrer is not available
    referrer = request.referrer
    if referrer:
        return redirect(referrer), 302
    else:
        return redirect(url_for('home')), 302
#--------------------------------------------------------------------
# Initialize database
with app.app_context():
    db.create_all()
    # Create admin user if not exists
    admin = User.query.get(1)
    if not admin:
        admin = User(id=1, mobile="0740694312", username="Administrator", allowed="yes")
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
    app.debug=True
    app.run()