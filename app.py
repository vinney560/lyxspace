import os
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
@app.route("/")
def home():
    return render_template("index.html")
#--------------------------------------------------------------------
@app.route("/login", methods=['GET', 'POST'])
def login():
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
    # Sample course data - in production, this would come from a database
    courses_data = [
        {
            'id': 1,
            'title': 'Ubuntu & Linux Mastery',
            'description': 'Complete guide to Linux command line, system administration, and shell scripting',
            'icon': 'fa-terminal',
            'level': 'Beginner to Advanced',
            'duration': '6 weeks',
            'lessons': 24,
            'category': 'System Administration',
            'color': 'from-green-500 to-emerald-600',
            'badge': 'Popular'
        },
        {
            'id': 2,
            'title': 'HTML5 & CSS3 Fundamentals',
            'description': 'Build modern, responsive websites with latest HTML5 and CSS3 features',
            'icon': 'fa-code',
            'level': 'Beginner',
            'duration': '4 weeks',
            'lessons': 18,
            'category': 'Web Development',
            'color': 'from-orange-500 to-red-500',
            'badge': 'Essential'
        },
        {
            'id': 3,
            'title': 'JavaScript Programming',
            'description': 'Master JavaScript from basics to advanced concepts and modern frameworks',
            'icon': 'fa-js-square',
            'level': 'Intermediate',
            'duration': '8 weeks',
            'lessons': 32,
            'category': 'Web Development',
            'color': 'from-yellow-500 to-amber-600',
            'badge': 'Hot'
        },
        {
            'id': 4,
            'title': 'Python Development',
            'description': 'Learn Python programming, web development with Django/Flask, and data science',
            'icon': 'fa-python',
            'level': 'Beginner to Advanced',
            'duration': '10 weeks',
            'lessons': 40,
            'category': 'Programming',
            'color': 'from-blue-500 to-cyan-500',
            'badge': 'Trending'
        },
        {
            'id': 5,
            'title': 'Linux Server Administration',
            'description': 'Advanced Linux server management, security, and deployment strategies',
            'icon': 'fa-server',
            'level': 'Advanced',
            'duration': '5 weeks',
            'lessons': 20,
            'category': 'System Administration',
            'color': 'from-purple-500 to-pink-500',
            'badge': 'Advanced'
        },
        {
            'id': 6,
            'title': 'Responsive Web Design',
            'description': 'Create mobile-first, responsive designs with CSS Grid, Flexbox, and frameworks',
            'icon': 'fa-laptop-code',
            'level': 'Intermediate',
            'duration': '3 weeks',
            'lessons': 12,
            'category': 'Web Development',
            'color': 'from-pink-500 to-rose-500',
            'badge': 'Design'
        }
    ]
    
    categories = list(set([course['category'] for course in courses_data]))
    
    return render_template("courses.html", courses=courses_data, categories=categories)

#--------------------------------------------------------------------
# Course Detail Route
@app.route("/course/<int:course_id>")
@login_required
def course_detail(course_id):
    # Sample course detail - in production, this would come from a database
    course_details = {
        1: {
            'title': 'Ubuntu & Linux Mastery',
            'description': 'Complete guide to Linux command line, system administration, and shell scripting',
            'long_description': 'This comprehensive course takes you from Linux beginner to proficient system administrator. You\'ll learn essential command line skills, file system management, user administration, networking, security, and automation with shell scripting.',
            'icon': 'fa-terminal',
            'level': 'Beginner to Advanced',
            'duration': '6 weeks',
            'lessons': 24,
            'projects': 5,
            'category': 'System Administration',
            'color': 'from-green-500 to-emerald-600',
            'instructor': 'Alex Johnson',
            'rating': 4.8,
            'students': 1250,
            'price': '$49.99',
            'modules': [
                {'title': 'Linux Fundamentals', 'lessons': 6, 'duration': '2 weeks'},
                {'title': 'Command Line Mastery', 'lessons': 5, 'duration': '1.5 weeks'},
                {'title': 'File System Management', 'lessons': 4, 'duration': '1 week'},
                {'title': 'User & Permission Management', 'lessons': 3, 'duration': '1 week'},
                {'title': 'Networking & Security', 'lessons': 3, 'duration': '1 week'},
                {'title': 'Shell Scripting', 'lessons': 3, 'duration': '1.5 weeks'}
            ],
            'resources': 15,
            'quizzes': 6
        },
        2: {
            'title': 'HTML5 & CSS3 Fundamentals',
            'description': 'Build modern, responsive websites with latest HTML5 and CSS3 features',
            'long_description': 'Start your web development journey with this comprehensive HTML5 and CSS3 course. Learn semantic HTML, CSS layouts, responsive design, animations, and modern web development practices.',
            'icon': 'fa-code',
            'level': 'Beginner',
            'duration': '4 weeks',
            'lessons': 18,
            'projects': 4,
            'category': 'Web Development',
            'color': 'from-orange-500 to-red-500',
            'instructor': 'Sarah Miller',
            'rating': 4.6,
            'students': 890,
            'price': '$39.99',
            'modules': [
                {'title': 'HTML5 Basics', 'lessons': 4, 'duration': '1 week'},
                {'title': 'CSS3 Fundamentals', 'lessons': 5, 'duration': '1 week'},
                {'title': 'Layouts & Positioning', 'lessons': 4, 'duration': '1 week'},
                {'title': 'Responsive Design', 'lessons': 3, 'duration': '1 week'},
                {'title': 'Advanced CSS Features', 'lessons': 2, 'duration': '1 week'}
            ],
            'resources': 12,
            'quizzes': 4
        }
    }
    
    course = course_details.get(course_id)
    if not course:
        flash("Course not found", "error")
        return redirect(url_for('courses'))
    
    return render_template("course_detail.html", course=course)

#--------------------------------------------------------------------
# Enroll in Course Route
@app.route("/course/<int:course_id>/enroll", methods=['POST'])
@login_required
def enroll_course(course_id):
    # In production, this would add the user to the course in the database
    flash(f"Successfully enrolled in the course!", "success")
    return redirect(url_for('course_detail', course_id=course_id))
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
    app.run(debug=True)