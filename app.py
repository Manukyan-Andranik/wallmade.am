import os
import json
# Mail imports
from flask_mail import Mail, Message

# Flask APP imports
import socket
import datetime
from functools import wraps
from werkzeug.security import  check_password_hash
from flask_babel import Babel, gettext as _, lazy_gettext as _l
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

# MongoDB imports
from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.errors import ConfigurationError, ConnectionFailure, ServerSelectionTimeoutError

# Cloudinary imports
import cloudinary
from cloudinary import CloudinaryImage
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

# My Modules imports
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']


# Mail configuration
MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER, DEFAULT_INSTRUCTOR_PHOTO = Config.load_env()
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = MAIL_DEFAULT_SENDER

mail = Mail(app)


# Initialize Babel for translations
babel = Babel(app)

# Cloudinary configuration
cloudinary.config(
    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
    api_key=app.config['CLOUDINARY_API_KEY'],
    api_secret=app.config['CLOUDINARY_API_SECRET']
)
LANGUAGES = app.config['LANGUAGES']

# Get Database using MongoDB client URI
def get_db():
    """Get MongoDB database connection with error handling"""
    try:
        client = MongoClient(
            app.config['MONGO_URI'],
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=30000,        # 30 second connection timeout
            socketTimeoutMS=30000          # 30 second socket timeout
        )
        # Test the connection
        client.server_info()
        return client.wallmade
    except (ConfigurationError, ConnectionFailure, ServerSelectionTimeoutError, socket.gaierror) as e:
        # Log the error and raise it to be caught by our error handler
        app.logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

# Get all collections from MongoDB
def get_collections():
    """Get all required collections"""
    db = get_db()
    return (
        db.products,
        db.works,
        db.admins,
        db.employees
    )

@app.errorhandler(ConfigurationError)
@app.errorhandler(ConnectionFailure)
@app.errorhandler(ServerSelectionTimeoutError)
@app.errorhandler(socket.gaierror)  # For DNS resolution errors
def handle_db_connection_error(e):
    error_message = "We're having trouble connecting to our database. Please try again later."
    if isinstance(e, ConfigurationError):
        error_message = "Database configuration error occurred. Our team has been notified."
    elif isinstance(e, (ConnectionFailure, ServerSelectionTimeoutError)):
        error_message = "Could not connect to the database. Please check your internet connection and try again."
    elif isinstance(e, socket.gaierror):
        error_message = "DNS resolution failed. Please check your network settings."
    
    # Log the error for debugging
    app.logger.error(f"Database connection error: {str(e)}")
    
    return render_template('error.html', 
                        error_code=503,
                        error_message=error_message), 503

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', 
                         error_code=500,
                         error_message="Something went wrong, please try again later"), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', 
                         error_code=404,
                         error_message="The page you're looking for doesn't exist"), 404

@babel.localeselector
def get_locale():
    # Check if language is set in session
    if 'language' in session:
        return session['language']
    # Fallback to browser language
    return request.accept_languages.best_match(LANGUAGES.keys())

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
    featured_products = list(products.find().limit(3))
    featured_works = list(works.find().limit(3))
    
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
    services = [{
        "en": {"title": "Custom Architectural Details", "icon": "design", "description": "Tailored solutions for unique architectural elements."},
        "ru": {"title": "Индивидуальные Архитектурные Элементы", "icon": "design", "description": "Персонализированные решения для уникальных архитектурных элементов."},
        "hy": {"title": "Անհատական Ճարտարապետական Մանրամասներ", "icon": "design", "description": "Անհատականացված լուծումներ յուրահատուկ ճարտարապետական տարրերի համար։"}
        }, 
        {"en": {"title": "Mass Production", "icon": "factory", "description": "High-quality, consistent production of architectural components."},
        "ru": {"title": "Массовое Производство", "icon": "factory", "description": "Высококачественное, стандартизированное производство архитектурных компонентов."},
        "hy": {"title": "Զանգվածային Արտադրություն", "icon": "factory", "description": "Ճարտարապետական բաղադրիչների բարձրորակ, հավասարաչափ արտադրություն։"}
        },
        {"en": {"title": "Design Consultation", "icon": "consult", "description": "Expert advice on material selection and design integration."},
        "ru": {"title": "Дизайн-Консультации", "icon": "consult", "description": "Экспертные рекомендации по подбору материалов и интеграции дизайна."},
        "hy": {"title": "Դիզայնի Խորհրդատվություն", "icon": "consult", "description": "Փորձագիտական խորհրդատվություն նյութերի ընտրության և դիզայնի ինտեգրման վերաբերյալ։"}
        },
        {"en": {"title": "Installation Support", "icon": "install", "description": "Professional guidance for proper installation."},
        "ru": {"title": "Поддержка Монтажа", "icon": "install", "description": "Профессиональное руководство по правильной установке."},
        "hy": {"title": "Տեղադրման Աջակցություն", "icon": "install", "description": "Պրոֆեսիոնալ ուղղորդում ճիշտ տեղադրման համար։"}
        }]
    return render_template('services.html', services=services, languages=LANGUAGES, current_language=get_locale())

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        subject = request.form.get('subject')
        phone = request.form.get('phone')
        print(name, email, message, subject, phone)
        if not all([name, email, subject, phone]):
            flash(_('Please fill all required fields'), 'error')
            return redirect(url_for('contact'))
        
        try:
            # Send email to admin
            msg = Message(
                subject=subject,
                recipients=[os.getenv('ADMIN_EMAIL')],
                body=f"""
                Name: {name}
                Email: {email}
                Phone: {phone}
                Subject: {subject}
                Message: {message}
                Sent from Wallmade Contact Form
                """
            )
            mail.send(msg)
            flash(_('Your message has been sent successfully! We will get back to you soon.'), 'success')
            return redirect(url_for('contact'))
            
        except Exception as e:
            app.logger.error(f"Failed to send email: {str(e)}")
            flash(_('Failed to send your message. Please try again later.'), 'error')
            return redirect(url_for('contact'))
    
    return render_template('contact.html', 
                         languages=LANGUAGES, 
                         current_language=get_locale())

@app.route('/products')
def products():
    products, _, _, _ = get_collections()
    all_products = list(products.find())
    return render_template('products.html', products=all_products, languages=LANGUAGES, current_language=get_locale())

@app.route('/product/<product_id>')
def product_detail(product_id):
    products, _, _, _ = get_collections()
    product = products.find_one({"_id": ObjectId(product_id)})
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
    print(work_id)
    _, works, _, _ = get_collections()
    work = works.find_one({"_id": ObjectId(work_id)})
    if not work:
        return redirect(url_for('works'))
    return render_template('work_detail.html', work=work, languages=LANGUAGES, current_language=get_locale())

# Admin Routes
@app.route('/admin')
def admin():
    if 'admin_logged_in' in session:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_login'))

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

@app.route('/admin/products/edit/<product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    try:
        products, _, _, _ = get_collections()
        product = products.find_one({"_id": ObjectId(product_id)})
        
        if not product:
            flash('Product not found', 'error')
            return redirect(url_for('admin_products'))
        
        if request.method == 'POST':
            # Handle multilingual fields
            title = {
                'en': request.form.get('title_en', ''),
                'hy': request.form.get('title_hy', ''),
                'ru': request.form.get('title_ru', '')
            }
            
            description = {
                'en': request.form.get('description_en', ''),
                'hy': request.form.get('description_hy', ''),
                'ru': request.form.get('description_ru', '')
            }
            
            # Handle features as array
            features = {
                'en': [f.strip() for f in request.form.get('features_en', '').split('\n') if f.strip()],
                'hy': [f.strip() for f in request.form.get('features_hy', '').split('\n') if f.strip()],
                'ru': [f.strip() for f in request.form.get('features_ru', '').split('\n') if f.strip()]
            }
            specifications = {
                'en': [f.strip() for f in request.form.get('specifications_en', '').split('\n') if f.strip()],
                'hy': [f.strip() for f in request.form.get('specifications_hy', '').split('\n') if f.strip()],
                'ru': [f.strip() for f in request.form.get('specifications_ru', '').split('\n') if f.strip()]
            }
            
            updates = {
                'title': title,
                'Images_folder_url': request.form.get('images_folder_url', ''),
                'description': description,
                'category': {
                    'en': request.form.get('category_en', ''),
                    'hy': request.form.get('category_hy', ''),
                    'ru': request.form.get('category_ru', '')
                },
                'material': {
                    'en': request.form.get('material_en', ''),
                    'hy': request.form.get('material_hy', ''),
                    'ru': request.form.get('material_ru', '')
                },
                'features': features,
                'specifications': specifications
            }
            
            # Update product
            result = products.update_one(
                {'_id': product['_id']},
                {'$set': updates}
            )
            
            flash('Product updated successfully', 'success')
            return redirect(url_for('admin_edit_product', product_id=product_id))
        
        return render_template('admin/edit_product.html', product=product)
        
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('admin_products'))
    
@app.route('/admin/products/delete/<product_id>')
@admin_required
def admin_delete_product(product_id):
    products, _, _, _ = get_collections()
    result = products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count > 0:
        flash('Product deleted successfully', 'success')
    else:
        flash('Product not found', 'error')
    return redirect(url_for('admin_products'))

@app.route('/admin/products/add')
@admin_required
def admin_add_product(product_id):
    products, _, _, _ = get_collections()
    result = products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count > 0:
        flash('Product deleted successfully', 'success')
    else:
        flash('Product not found', 'error')
    return redirect(url_for('admin_products'))


@app.route('/admin/works')
@admin_required
def admin_works():
    _, works, _, _ = get_collections()
    all_works = list(works.find())
    return render_template('admin/works.html', works=all_works, languages=LANGUAGES, current_language=get_locale())

@app.route('/admin/works/add', methods=['GET', 'POST'])
@admin_required
def admin_add_work():
    _, works, _, _ = get_collections()
    
    if request.method == 'POST':
        try:
            # Handle multilingual fields
            title = {
                'en': request.form.get('title_en', ''),
                'hy': request.form.get('title_hy', ''),
                'ru': request.form.get('title_ru', '')
            }
            
            description = {
                'en': request.form.get('description_en', ''),
                'hy': request.form.get('description_hy', ''),
                'ru': request.form.get('description_ru', '')
            }
            
            location = {
                'en': request.form.get('location_en', ''),
                'hy': request.form.get('location_hy', ''),
                'ru': request.form.get('location_ru', '')
            }
            
            project_type = {
                'en': request.form.get('project_type_en', ''),
                'hy': request.form.get('project_type_hy', ''),
                'ru': request.form.get('project_type_ru', '')
            }
            
            architect = {
                'en': request.form.get('architect_en', ''),
                'hy': request.form.get('architect_hy', ''),
                'ru': request.form.get('architect_ru', '')
            }
            
            # Handle products used as arrays
            products_used = {
                'en': [f.strip() for f in request.form.get('products_used_en', '').split('\n') if f.strip()],
                'hy': [f.strip() for f in request.form.get('products_used_hy', '').split('\n') if f.strip()],
                'ru': [f.strip() for f in request.form.get('products_used_ru', '').split('\n') if f.strip()]
            }
            
            # Handle testimonial
            testimonial_text = {
                'en': request.form.get('testimonial_text_en', ''),
                'hy': request.form.get('testimonial_text_hy', ''),
                'ru': request.form.get('testimonial_text_ru', '')
            }
            
            testimonial_position = {
                'en': request.form.get('testimonial_position_en', ''),
                'hy': request.form.get('testimonial_position_hy', ''),
                'ru': request.form.get('testimonial_position_ru', '')
            }
            
            testimonial = None
            if request.form.get('testimonial_author'):
                testimonial = {
                    'text': testimonial_text,
                    'author': request.form.get('testimonial_author', ''),
                    'position': testimonial_position
                }
            
            # Create new work data
            new_work = {
                '_id': ObjectId(),
                'title': title,
                'Images_folder_url': request.form.get('image', ''),
                'description': description,
                'location': location,
                'project_type': project_type,
                'year': request.form.get('year', ''),
                'architect': architect,
                'products_used': products_used,
                'testimonial': testimonial,
                'created_at': datetime.datetime.utcnow(),
                'updated_at': datetime.datetime.utcnow()
            }
            
            # Handle image upload if present
            if 'image' in request.files and request.files['image'].filename != '':
                image = request.files['image']
                upload_result = upload(image)
                new_work['Images_folder_url'] = upload_result['secure_url']
            
            # Insert the new work
            works.insert_one(new_work)
            
            flash('Work created successfully!', 'success')
            return redirect(url_for('admin_works'))
            
        except Exception as e:
            flash(f'Error creating work: {str(e)}', 'error')
            return redirect(url_for('admin_add_work'))
    
    # GET request - show empty form
    empty_work = {
        'title': {'en': '', 'hy': '', 'ru': ''},
        'description': {'en': '', 'hy': '', 'ru': ''},
        'location': {'en': '', 'hy': '', 'ru': ''},
        'project_type': {'en': '', 'hy': '', 'ru': ''},
        'architect': {'en': '', 'hy': '', 'ru': ''},
        'products_used': {'en': [], 'hy': [], 'ru': []},
        'Images_folder_url': '',
        'year': '',
        'testimonial': None
    }
    
    return render_template('admin/edit_work.html', work=empty_work, is_new=True)

@app.route('/admin/works/edit/<work_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_work(work_id):
    try:
        _, works, _, _ = get_collections()
        work = works.find_one({"_id": ObjectId(work_id)})
        
        if not work:
            flash('Work not found', 'error')
            return redirect(url_for('admin_works'))
        
        if request.method == 'POST':
            # Handle multilingual fields
            title = {
                'en': request.form.get('title_en', ''),
                'hy': request.form.get('title_hy', ''),
                'ru': request.form.get('title_ru', '')
            }
            
            description = {
                'en': request.form.get('description_en', ''),
                'hy': request.form.get('description_hy', ''),
                'ru': request.form.get('description_ru', '')
            }
            
            location = {
                'en': request.form.get('location_en', ''),
                'hy': request.form.get('location_hy', ''),
                'ru': request.form.get('location_ru', '')
            }
            
            project_type = {
                'en': request.form.get('project_type_en', ''),
                'hy': request.form.get('project_type_hy', ''),
                'ru': request.form.get('project_type_ru', '')
            }
            
            architect = {
                'en': request.form.get('architect_en', ''),
                'hy': request.form.get('architect_hy', ''),
                'ru': request.form.get('architect_ru', '')
            }
            
            # Handle products used as arrays
            products_used = {
                'en': [f.strip() for f in request.form.get('products_used_en', '').split('\n') if f.strip()],
                'hy': [f.strip() for f in request.form.get('products_used_hy', '').split('\n') if f.strip()],
                'ru': [f.strip() for f in request.form.get('products_used_ru', '').split('\n') if f.strip()]
            }
            
            # Handle testimonial
            testimonial_text = {
                'en': request.form.get('testimonial_text_en', ''),
                'hy': request.form.get('testimonial_text_hy', ''),
                'ru': request.form.get('testimonial_text_ru', '')
            }
            
            testimonial_position = {
                'en': request.form.get('testimonial_position_en', ''),
                'hy': request.form.get('testimonial_position_hy', ''),
                'ru': request.form.get('testimonial_position_ru', '')
            }
            
            testimonial = None
            if request.form.get('testimonial_author'):
                testimonial = {
                    'text': testimonial_text,
                    'author': request.form.get('testimonial_author', ''),
                    'position': testimonial_position
                }
            
            updates = {
                'title': title,
                'description': description,
                'location': location,
                'project_type': project_type,
                'year': request.form.get('year', ''),
                'architect': architect,
                'products_used': products_used,
                'testimonial': testimonial,
                'updated_at': datetime.datetime.utcnow()
            }
            
            # Handle image URL or upload
            if request.form.get('image'):
                updates['Images_folder_url'] = request.form.get('image')
            
            if 'image' in request.files and request.files['image'].filename != '':
                image = request.files['image']
                upload_result = upload(image)
                updates['Images_folder_url'] = upload_result['secure_url']
            
            # Update work
            works.update_one(
                {'_id': work['_id']},
                {'$set': updates}
            )
            
            flash('Work updated successfully', 'success')
            return redirect(url_for('admin_edit_work', work_id=work_id))
        
        return render_template('admin/edit_work.html', work=work, is_new=False)
        
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('admin_works'))

@app.route('/admin/works/delete/<work_id>')
@admin_required
def admin_delete_work(work_id):
    try:
        _, works, _, _ = get_collections()
        result = works.delete_one({"_id": ObjectId(work_id)})
        
        if result.deleted_count == 1:
            flash('Work deleted successfully', 'success')
        else:
            flash('Work not found', 'error')
            
        return redirect(url_for('admin_works'))
    except Exception as e:
        flash(f'Error deleting work: {str(e)}', 'error')
        return redirect(url_for('admin_works'))

# ... (keep all your existing imports and configuration) ...

@app.route('/admin/json-insert', methods=['GET', 'POST'])
@admin_required
def admin_json_insert():
    """Admin route for inserting JSON data into any collection"""
    if request.method == 'POST':
        try:
            # Get all collections
            products, works, admins, employees = get_collections()
            
            # Get form data
            collection_name = request.form.get('collection')
            json_data = request.form.get('json_data')
            
            # Validate inputs
            if not collection_name or not json_data:
                flash('Please select a collection and provide JSON data', 'error')
                return redirect(url_for('admin_json_insert'))
            
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError as e:
                flash(f'Invalid JSON: {str(e)}', 'error')
                return redirect(url_for('admin_json_insert'))
            
            # Determine which collection to use
            collection_map = {
                'products': products,
                'works': works,
                'admins': admins,
                'employees': employees
            }
            
            if collection_name not in collection_map:
                flash('Invalid collection selected', 'error')
                return redirect(url_for('admin_json_insert'))
            
            collection = collection_map[collection_name]
            
            # Insert the data
            if isinstance(data, list):
                result = collection.insert_many(data)
                inserted_ids = [str(id) for id in result.inserted_ids]
                flash(f'Successfully inserted {len(inserted_ids)} documents', 'success')
            else:
                result = collection.insert_one(data)
                inserted_ids = [str(result.inserted_id)]
                flash('Document inserted successfully', 'success')
            
            # Store the result in session to display on the page
            session['last_insert_result'] = {
                'collection': collection_name,
                'inserted_ids': inserted_ids,
                'count': len(inserted_ids)
            }
            
            return redirect(url_for('admin_json_insert'))
            
        except Exception as e:
            flash(f'Error inserting data: {str(e)}', 'error')
            return redirect(url_for('admin_json_insert'))
    
    # GET request - show the form
    last_result = session.pop('last_insert_result', None)
    return render_template('admin/json_insert.html',
                         last_result=last_result,
                         languages=LANGUAGES,
                         current_language=get_locale())
    
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)