from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, g
from flask_pymongo import PyMongo
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from cloudinary import CloudinaryImage
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
import os
from config import Config
from bson.objectid import ObjectId
from flask_babel import Babel, gettext as _, lazy_gettext as _l
import gettext

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Initialize Babel for translations
babel = Babel(app)

# Configure available languages
LANGUAGES = {
    'en': 'English',
    'hy': 'Հայերեն',
    'ru': 'Русский'
}

@babel.localeselector
def get_locale():
    # Check if language is set in session
    if 'language' in session:
        return session['language']
    # Fallback to browser language
    return request.accept_languages.best_match(LANGUAGES.keys())

def get_db():
    """Get MongoDB database connection"""
    client = MongoClient(app.config['MONGO_URI'])
    db = client.wallmade
    return db

def get_collections():
    """Get all required collections"""
    db = get_db()
    return (
        db.products,
        db.works,
        db.admins,
        db.employees
    )

# Cloudinary configuration
import cloudinary
cloudinary.config(
    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
    api_key=app.config['CLOUDINARY_API_KEY'],
    api_secret=app.config['CLOUDINARY_API_SECRET']
)

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Language route
@app.route('/set_language/<language>')
def set_language(language):
    if language in LANGUAGES:
        session['language'] = language
    return redirect(request.referrer or url_for('home'))

# Frontend Routes
@app.route('/')
def home():
    products, works, _, _ = get_collections()
    featured_products = list(products.find().limit(4))
    featured_works = list(works.find().limit(4))
    
    return render_template('index.html',
                         featured_products=featured_products,
                         featured_works=featured_works,
                         languages=LANGUAGES,
                         current_language=get_locale())

@app.route('/about')
def about():
    _, _, _, employees = get_collections()
    employees = list(employees.find())
    return render_template('about.html', employees=employees, languages=LANGUAGES, current_language=get_locale())

@app.route('/services')
def services():
    services = [
        {"title": "Custom Architectural Details", "icon": "design", "description": "Tailored solutions for unique architectural elements."},
        {"title": "Mass Production", "icon": "factory", "description": "High-quality, consistent production of architectural components."},
        {"title": "Design Consultation", "icon": "consult", "description": "Expert advice on material selection and design integration."},
        {"title": "Installation Support", "icon": "install", "description": "Professional guidance for proper installation."}
    ]
    return render_template('services.html', services=services, languages=LANGUAGES, current_language=get_locale())

@app.route('/products')
def products():
    products, _, _, _ = get_collections()
    all_products = list(products.find())
    return render_template('products.html', products=all_products, languages=LANGUAGES, current_language=get_locale())

@app.route('/product/<product_id>')
def product_detail(product_id):
    products, _, _, _ = get_collections()
    product = products.find_one({"_id": product_id})
    if not product:
        return redirect(url_for('products'))
    return render_template('product_detail.html', product=product, languages=LANGUAGES, current_language=get_locale())

@app.route('/works')
def works():
    _, works, _, _ = get_collections()
    all_works = list(works.find())
    return render_template('works.html', works=all_works, languages=LANGUAGES, current_language=get_locale())

@app.route('/work/<work_id>')
def work_detail(work_id):
    _, works, _, _ = get_collections()
    work = works.find_one({"_id": work_id})
    if not work:
        return redirect(url_for('works'))
    return render_template('work_detail.html', work=work, languages=LANGUAGES, current_language=get_locale())

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        print(f"New contact from {name} ({email}): {message}")
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', languages=LANGUAGES, current_language=get_locale())

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        _, _, admins, _ = get_collections()
        print(username, password)
        
        admin_user = admins.find_one({"username": username, "is_admin": "True"})
        print(admin_user)
        if admin_user and check_password_hash(admin_user['password'], password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('admin/login.html', languages=LANGUAGES, current_language=get_locale())

@app.route('/admin/logout')
@admin_required
def admin_logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('admin_login'), languages=LANGUAGES, current_language=get_locale())

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html', languages=LANGUAGES, current_language=get_locale())

@app.route('/admin/products')
@admin_required
def admin_products():
    products, _, _, _ = get_collections()
    
    if request.method == 'POST':
        # Handle product creation or update
        product_id = request.form.get('product_id')
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        material = request.form.get('material')
        
        product_data = {
            "title": title,
            "description": description,
            "category": category,
            "material": material,
            "features": request.form.get('features', '').split('\n'),
            "specifications": []
        }
        
        # Handle specifications if provided
        spec_names = request.form.getlist('spec_name[]')
        spec_values = request.form.getlist('spec_value[]')
        for name, value in zip(spec_names, spec_values):
            if name and value:
                product_data["specifications"].append({"name": name, "value": value})
        
        # Handle image upload
        if 'image' in request.files and request.files['image'].filename != '':
            image = request.files['image']
            upload_result = upload(image)
            product_data["Images_folder_url"] = upload_result['secure_url']
        
        if product_id:
            # Update existing product
            products.update_one({"_id": product_id}, {"$set": product_data})
            flash('Product updated successfully!', 'success')
        else:
            # Create new product
            product_data["_id"] = str(ObjectId())
            products.insert_one(product_data)
            flash('Product created successfully!', 'success')
        
        return redirect(url_for('admin_products'))
    
    all_products = list(products.find())
    return render_template('admin/products.html', products=all_products, languages=LANGUAGES, current_language=get_locale())

@app.route('/admin/product/delete/<product_id>')
@admin_required
def admin_delete_product(product_id):
    products, _, _, _ = get_collections()
    products.delete_one({"_id": product_id})
    flash('Product deleted successfully', 'success')
    return redirect(url_for('admin_products'), languages=LANGUAGES, current_language=get_locale())

@app.route('/admin/works', methods=['GET', 'POST'])
@admin_required
def admin_works():
    _, works, _, _ = get_collections()
    
    if request.method == 'POST':
        # Handle work creation or update
        work_id = request.form.get('work_id')
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        project_type = request.form.get('project_type')
        year = request.form.get('year')
        architect = request.form.get('architect')
        
        work_data = {
            "title": title,
            "description": description,
            "location": location,
            "project_type": project_type,
            "year": year,
            "architect": architect,
            "products_used": request.form.get('products_used', '').split('\n')
        }
        
        # Handle testimonial if provided
        testimonial_text = request.form.get('testimonial_text')
        testimonial_author = request.form.get('testimonial_author')
        testimonial_position = request.form.get('testimonial_position')
        
        if testimonial_text and testimonial_author:
            work_data["testimonial"] = {
                "text": testimonial_text,
                "author": testimonial_author,
                "position": testimonial_position
            }
        
        # Handle image upload
        if 'image' in request.files and request.files['image'].filename != '':
            image = request.files['image']
            upload_result = upload(image)
            work_data["Images_folder_url"] = upload_result['secure_url']
        
        if work_id:
            # Update existing work
            works.update_one({"_id": work_id}, {"$set": work_data})
            flash('Work updated successfully!', 'success')
        else:
            # Create new work
            work_data["_id"] = str(ObjectId())
            works.insert_one(work_data)
            flash('Work created successfully!', 'success')
        
        return redirect(url_for('admin_works'))
    
    all_works = list(works.find())
    return render_template('admin/works.html', works=all_works, languages=LANGUAGES, current_language=get_locale())

@app.route('/admin/work/delete/<work_id>')
@admin_required
def admin_delete_work(work_id):
    _, works, _, _ = get_collections()
    works.delete_one({"_id": work_id})
    flash('Work deleted successfully', 'success')
    return redirect(url_for('admin_works'), languages=LANGUAGES, current_language=get_locale())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)