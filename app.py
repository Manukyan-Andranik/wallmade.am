import os
import json
from datetime import datetime
# Mail imports
from flask_mail import Mail, Message
from bson import json_util

# Flask APP imports
import socket
import datetime
from functools import wraps
from werkzeug.security import check_password_hash
from flask_babel import Babel, gettext as _, lazy_gettext as _l
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

# MongoDB imports
# from pymongo import MongoClient
from bson.objectid import ObjectId
# from pymongo.errors import ConfigurationError, ConnectionFailure, ServerSelectionTimeoutError

# Cloudinary imports
import cloudinary
from cloudinary import CloudinaryImage
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

# My Modules imports
from config import Config, VideoConfig
from data_manager import DataManager
from logger import AppLogger

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Initialize logger
logger = AppLogger(app)

# Mail configuration
MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USE_SSL, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER = Config.load_env()
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
app.config['MAIL_USE_SSL'] = MAIL_USE_SSL
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = MAIL_DEFAULT_SENDER
mail = Mail(app)

# Initialize Babel for translations
babel = Babel(app)
LANGUAGES = app.config['LANGUAGES']

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f'Internal Server Error: {str(e)}', exc_info=True)
    return render_template('error.html', 
                         error_code=500,
                         error_message="Something went wrong, please try again later"), 500

@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning(f'Page not found: {request.url}')
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
            app.logger.warning(f'Unauthorized access attempt to {request.url}')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Language route
@app.route('/set_language/<language>')
def set_language(language):
    if language in LANGUAGES:
        session['language'] = language
        app.logger.info(f'Language set to {language} for session')
    return redirect(request.referrer or url_for('home'))

# Frontend Routes
@app.route('/')
def home():
    try:
        products = DataManager.get_collection_from_json("products")
        works = DataManager.get_collection_from_json("works")
        featured_products = products[:3]
        featured_works = works[:3]
        
        for i, work in enumerate(featured_works):
            featured_works[i]["Images_folder_url"] = Config.fetch_work_images_by_folder(work['Images_folder_url'])[0]
        
        app.logger.info('Home page loaded successfully')
        return render_template('index.html',
                            featured_products=featured_products,
                            featured_works=featured_works,
                            languages=LANGUAGES,
                            current_language=get_locale())
    except Exception as e:
        app.logger.error(f'Error loading home page: {str(e)}', exc_info=True)
        raise

@app.route('/about')
def about():
    try:
        employees = DataManager.get_collection_from_json("employees")
        app.logger.info('About page loaded successfully')
        return render_template('about.html', employees=employees, languages=LANGUAGES, current_language=get_locale())
    except Exception as e:
        app.logger.error(f'Error loading about page: {str(e)}', exc_info=True)
        raise

@app.route('/services')
def services():
    try:
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
        app.logger.info('Services page loaded successfully')
        return render_template('services.html', services=services, languages=LANGUAGES, current_language=get_locale())
    except Exception as e:
        app.logger.error(f'Error loading services page: {str(e)}', exc_info=True)
        raise

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        subject = request.form.get('subject')
        phone = request.form.get('phone')

        if not all([name, email, subject, phone]):
            app.logger.warning('Contact form submission missing required fields')
            flash(_('Please fill all required fields.'), 'error')
            return redirect(url_for('contact'))

        try:
            msg = Message(
                subject=f"[Wallmade Contact] {subject}",
                sender=os.getenv('MAIL_DEFAULT_SENDER'),
                recipients=[os.getenv('ADMIN_EMAIL')],
                body=f"""
Wallmade Contact Form Submission

Name: {name}
Email: {email}
Phone: {phone}
Subject: {subject}

Message:
{message}

Sent from Wallmade.am contact form.
                """
            )
            mail.send(msg)
            app.logger.info(f'Contact form submitted successfully from {email}')
            flash(_('Your message has been sent successfully! We will get back to you soon.'), 'success')
        except Exception as e:
            app.logger.error(f"Email send failed: {str(e)}", exc_info=True)
            flash(_('Failed to send your message. Please try again later.'), 'error')

        return redirect(url_for('contact'))

    app.logger.info('Contact page loaded')
    return render_template('contact.html', 
                           languages=LANGUAGES, 
                           current_language=get_locale())

@app.route('/products')
def products():
    try:
        all_products = DataManager.get_collection_from_json("products")
        app.logger.info('Products page loaded successfully')
        return render_template('products.html', products=all_products, languages=LANGUAGES, current_language=get_locale())
    except Exception as e:
        app.logger.error(f'Error loading products page: {str(e)}', exc_info=True)
        raise

@app.route('/product/<product_id>')
def product_detail(product_id):
    try:
        product = DataManager.get_item_from_json_by_id("products", product_id)
        if not product:
            app.logger.warning(f'Product not found with ID: {product_id}')
            return redirect(url_for('products'))
        
        app.logger.info(f'Product detail page loaded for product ID: {product_id}')
        return render_template('product_detail.html', product=product, languages=LANGUAGES, current_language=get_locale())
    except Exception as e:
        app.logger.error(f'Error loading product detail page: {str(e)}', exc_info=True)
        raise

@app.route('/works')
def works():
    try:
        all_works = DataManager.get_collection_from_json("works")
        for i, work in enumerate(all_works):
            all_works[i]["Images_folder_url"] = Config.fetch_work_images_by_folder(work['Images_folder_url'])
        partners = ["homeexpo.png", "viewbox.png"]
        app.logger.info('Works page loaded successfully')
        return render_template('works.html', partners=partners, works=all_works, languages=LANGUAGES, current_language=get_locale())
    except Exception as e:
        app.logger.error(f'Error loading works page: {str(e)}', exc_info=True)
        raise

@app.route('/work/<work_id>')
def work_detail(work_id):
    try:
        work = DataManager.get_item_from_json_by_id("works", work_id)
        if not work:
            app.logger.warning(f'Work not found with ID: {work_id}')
            return redirect(url_for('works'))
        
        images = Config.fetch_work_images_by_folder(work['Images_folder_url'])
        work['Images_folder_url'] = images
        app.logger.info(f'Work detail page loaded for work ID: {work_id}')
        return render_template('work_detail.html', work=work, languages=LANGUAGES, current_language=get_locale())
    except Exception as e:
        app.logger.error(f'Error loading work detail page: {str(e)}', exc_info=True)
        raise

# Admin Routes
@app.route('/admin')
def admin():
    if 'admin_logged_in' in session:
        app.logger.info(f'Admin {session["admin_username"]} accessed admin dashboard')
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admins = DataManager.get_collection_from_json("admins")
        
        admin_user = admins.find_one({"username": username, "is_admin": "True"})
        if admin_user and check_password_hash(admin_user['password'], password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            app.logger.info(f'Admin {username} logged in successfully')
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            app.logger.warning(f'Failed login attempt for username: {username}')
            flash('Invalid username or password', 'danger')
    
    app.logger.info('Admin login page accessed')
    return render_template('admin/login.html', languages=LANGUAGES, current_language=get_locale())

@app.route('/admin/logout')
@admin_required
def admin_logout():
    username = session.get('admin_username', 'unknown')
    session.clear()
    app.logger.info(f'Admin {username} logged out')
    flash('You have been logged out', 'info')
    return redirect(url_for('admin_login'), languages=LANGUAGES, current_language=get_locale())

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    app.logger.info(f'Admin dashboard accessed by {session["admin_username"]}')
    return render_template('admin/dashboard.html', languages=LANGUAGES, current_language=get_locale())

@app.route('/admin/products')
@admin_required
def admin_products():
    try:
        all_products = DataManager.get_collection_from_json("products")
        app.logger.info(f'Admin products page accessed by {session["admin_username"]}')
        return render_template('admin/products.html', products=all_products, languages=LANGUAGES, current_language=get_locale())
    except Exception as e:
        app.logger.error(f'Error loading admin products: {str(e)}', exc_info=True)
        raise

@app.route('/admin/products/edit/<product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    try:
        product = DataManager.get_item_from_json_by_id("products", product_id)
        
        if not product:
            app.logger.warning(f'Product not found for editing: {product_id}')
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
            
            app.logger.info(f'Product {product_id} updated by {session["admin_username"]}')
            flash('Product updated successfully', 'success')
            return redirect(url_for('admin_edit_product', product_id=product_id))
        
        app.logger.info(f'Product edit page loaded for product ID: {product_id}')
        return render_template('admin/edit_product.html', product=product)
        
    except Exception as e:
        app.logger.error(f'Error editing product: {str(e)}', exc_info=True)
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('admin_products'))
    
@app.route('/admin/products/delete/<product_id>')
@admin_required
def admin_delete_product(product_id):
    try:
        success = DataManager.delete_item_from_json_by_id("products", product_id)
        if not success:
            app.logger.warning(f'Product not found for deletion: {product_id}')
            flash('Product not found', 'error')
            return "Product not found", 404
        
        app.logger.info(f'Product {product_id} deleted by {session["admin_username"]}')
        flash('Product deleted successfully', 'success')
        return redirect(url_for('admin_products'))
    except Exception as e:
        app.logger.error(f'Error deleting product: {str(e)}', exc_info=True)
        flash(f'Error deleting product: {str(e)}', 'error')
        return redirect(url_for('admin_products'))

@app.route('/admin/works')
@admin_required
def admin_works():
    try:
        all_works = DataManager.get_collection_from_json("works")
        app.logger.info(f'Admin works page accessed by {session["admin_username"]}')
        return render_template('admin/works.html', works=all_works, languages=LANGUAGES, current_language=get_locale())
    except Exception as e:
        app.logger.error(f'Error loading admin works: {str(e)}', exc_info=True)
        raise

@app.route('/admin/works/edit/<work_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_work(work_id):
    try:
        work = DataManager.get_item_from_json_by_id("works", work_id)
        
        if not work:
            app.logger.warning(f'Work not found for editing: {work_id}')
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
            
            # Handle products used as arrays
            products_used = {
                'en': [f.strip() for f in request.form.get('products_used_en', '').split('\n') if f.strip()],
                'hy': [f.strip() for f in request.form.get('products_used_hy', '').split('\n') if f.strip()],
                'ru': [f.strip() for f in request.form.get('products_used_ru', '').split('\n') if f.strip()]
            }

            
            updates = {
                'title': title,
                'description': description,
                'location': location,
                'project_type': project_type,
                'year': request.form.get('year', ''),
                'products_used': products_used,
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
            
            app.logger.info(f'Work {work_id} updated by {session["admin_username"]}')
            flash('Work updated successfully', 'success')
            return redirect(url_for('admin_edit_work', work_id=work_id))
        
        app.logger.info(f'Work edit page loaded for work ID: {work_id}')
        return render_template('admin/edit_work.html', work=work, is_new=False)
        
    except Exception as e:
        app.logger.error(f'Error editing work: {str(e)}', exc_info=True)
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('admin_works'))

@app.route('/admin/works/delete/<work_id>')
@admin_required
def admin_delete_work(work_id):
    try:
        success = DataManager.delete_item_from_json_by_id("works", work_id)
        if not success:
            app.logger.warning(f'Work not found for deletion: {work_id}')
            flash('Work not found', 'error')
            return "Work not found", 404
        
        app.logger.info(f'Work {work_id} deleted by {session["admin_username"]}')
        flash('Work deleted successfully', 'success')
        return redirect(url_for('admin_works'))
    except Exception as e:
        app.logger.error(f'Error deleting work: {str(e)}', exc_info=True)
        flash(f'Error deleting work: {str(e)}', 'error')
        return redirect(url_for('admin_works'))

@app.route('/admin/json-insert', methods=['GET', 'POST'])
@admin_required
def admin_json_insert():
    """Admin route for inserting JSON data into a JSON file"""
    if request.method == 'POST':
        try:
            # Supported collections and their corresponding JSON files
            collection_files = {
                'products': 'products',
                'works': 'works',
                'admins': 'admins',
                'employees': 'employees'
            }

            # Get form data
            collection_name = request.form.get('collection')
            json_data = request.form.get('json_data')

            # Validate inputs
            if not collection_name or not json_data:
                flash('Please select a collection and provide JSON data', 'error')
                return redirect(url_for('admin_json_insert'))

            if collection_name not in collection_files:
                flash('Invalid collection selected', 'error')
                return redirect(url_for('admin_json_insert'))

            try:
                data = json.loads(json_data)
            except json.JSONDecodeError as e:
                flash(f'Invalid JSON: {str(e)}', 'error')
                return redirect(url_for('admin_json_insert'))

            filename = collection_files[collection_name]

            # Load existing data
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f, object_hook=json_util.object_hook)
            else:
                existing_data = []

            inserted_ids = []
            timestamp = datetime.datetime.utcnow()

            if isinstance(data, list):
                for doc in data:
                    doc['_id'] = ObjectId()
                    doc['created_at'] = timestamp
                    inserted_ids.append(str(doc['_id']))
                    existing_data.append(doc)
            else:
                data['_id'] = ObjectId()
                data['created_at'] = timestamp
                inserted_ids.append(str(data['_id']))
                existing_data.append(data)

            # Save updated data back to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, default=json_util.default, indent=2, ensure_ascii=False)

            flash(f'Successfully inserted {len(inserted_ids)} document(s)', 'success')
            app.logger.info(f'Admin {session["admin_username"]} inserted {len(inserted_ids)} documents into {collection_name}')

            session['last_insert_result'] = {
                'collection': collection_name,
                'inserted_ids': inserted_ids,
                'count': len(inserted_ids)
            }

            return redirect(url_for('admin_json_insert'))

        except Exception as e:
            app.logger.error(f'Error inserting JSON data: {str(e)}', exc_info=True)
            flash(f'Error inserting data: {str(e)}', 'error')
            return redirect(url_for('admin_json_insert'))

    # GET request
    last_result = session.pop('last_insert_result', None)
    app.logger.info(f'Admin JSON insert page accessed by {session["admin_username"]}')
    return render_template('admin/json_insert.html',
                           last_result=last_result,
                           languages=LANGUAGES,
                           current_language=get_locale())

if __name__ == '__main__':
    app.logger.info('Starting Wallmade application')
    app.run(host="0.0.0.0", port=5001, debug=True)