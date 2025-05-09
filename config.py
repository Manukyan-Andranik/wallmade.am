import os
import cloudinary
import cloudinary.api
import cloudinary.search
from dotenv import load_dotenv
from urllib.parse import quote_plus
load_dotenv()

class Config:
    """
    Configuration class for the application.
    This class loads environment variables from a .env file and sets up the necessary configurations for the application.
    It includes configurations for Cloudinary, MongoDB, and other necessary settings.
    The class also includes environment variables for initial admin setup.
    """
    # Cloudinary configuration
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

    # MongoDB configuration
    USER_NAME = os.getenv('MONGO_USERNAME')
    PASSWORD = os.getenv('MONGO_PASSWORD')
    escaped_username = quote_plus(USER_NAME)
    escaped_password = quote_plus(PASSWORD)
    MONGO_URI = f"mongodb+srv://{escaped_username}:{escaped_password}@cluster0.ckpsnux.mongodb.net/wallmade?retryWrites=true&w=majority&appName=Cluster0"
    
    # Admin credentials (for initial setup)
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

    # APP Languages
    LANGUAGES = {
    'hy': 'Հայերեն',
    'ru': 'Русский',
    'en': 'English'
    }

    def load_env():
        MAIL_SERVER = os.getenv('MAIL_SERVER')
        MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
        MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
        MAIL_USERNAME = os.getenv('MAIL_USERNAME')
        MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
        MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
        DEFAULT_INSTRUCTOR_PHOTO = os.getenv('DEFAULT_INSTRUCTOR_PHOTO')
        return MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER, DEFAULT_INSTRUCTOR_PHOTO

    def fetch_work_images():
        # Cloudinary config
        cloudinary.config(
            cloud_name=Config.CLOUDINARY_CLOUD_NAME,
            api_key=Config.CLOUDINARY_API_KEY,
            api_secret=Config.CLOUDINARY_API_SECRET,
        )
        base_folder = 'Works'
        result = {}

        # List subfolders in 'Works'
        folders = cloudinary.api.subfolders(base_folder)['folders']
        for folder in folders:
            folder_name = folder['name']  # e.g., work1, work2, etc.
            full_path = f"{base_folder}/{folder_name}"

            # Search for images in this folder
            search = cloudinary.Search().expression(f"folder:{full_path}").max_results(500)
            resources = search.execute()['resources']

            # Extract URLs
            image_urls = [resource['secure_url'] for resource in resources]

            # Add to result dictionary
            result[folder_name] = image_urls

        return result

    def fetch_work_images_by_folder(folder_name):
        # Cloudinary config
        cloudinary.config(
            cloud_name=Config.CLOUDINARY_CLOUD_NAME,
            api_key=Config.CLOUDINARY_API_KEY,
            api_secret=Config.CLOUDINARY_API_SECRET,
        )
        base_folder = 'Works'
        full_path = f"{base_folder}/{folder_name}"

        # Search for images in this folder
        search = cloudinary.Search().expression(f"folder:{full_path}").max_results(500)
        resources = search.execute()['resources']

        # Extract URLs
        image_urls = [resource['secure_url'] for resource in resources]

        return image_urls