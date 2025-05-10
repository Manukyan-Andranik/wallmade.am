import os
import cloudinary
import cloudinary.api
from dotenv import load_dotenv
from urllib.parse import quote_plus
load_dotenv()

class VideoConfig:
    video_data = [
    {
        'filename': 'reel1.mp4',
        'poster': 'back2.jpg',
        'title': {
            'en': 'Metal Panel Fabrication',
            'hy': 'Արտադրություն մետաղական պանելների',
            'ru': 'Изготовление металлических панелей'
        },
        'description': {
            'en': 'See how we craft our premium metal exterior panels from raw materials to finished product.',
            'hy': 'Դիտեք, թե ինչպես ենք մենք պատրաստում մեր բարձրորակ մետաղական արտաքին պանելները հումքից մինչև պատրաստի արտադրանք։',
            'ru': 'Посмотрите, как мы создаем наши премиальные металлические фасадные панели.'
        },
        'category': 'production',
        'duration': '1:00',
        'date': {
            'en': 'May 15, 2023',
            'hy': '2023թ. մայիսի 15',
            'ru': '15 мая 2023 г.'
        }
    },
    {
        'filename': 'reel2.mp4',
        'poster': 'back2.jpg',
        'title': {
            'en': 'Corner Detail Installation',
            'hy': 'Ոլոր անկյունային տարրի տեղադրում',
            'ru': 'Установка угловых элементов'
        },
        'description': {
            'en': 'Step-by-step demonstration of our specialized corner installation technique.',
            'hy': 'Քայլ առ քայլ ցուցադրում մեր անկյունների տեղադրման հատուկ տեխնիկայից։',
            'ru': 'Пошаговая демонстрация нашей специальной техники монтажа углов.'
        },
        'category': 'installation',
        'duration': '1:00',
        'date': {
            'en': 'June 2, 2023',
            'hy': '2023թ. հունիսի 2',
            'ru': '2 июня 2023 г.'
        }
    },
    {
        'filename': 'reel3.mp4',
        'poster': 'back2.jpg',
        'title': {
            'en': 'Quality Control Process',
            'hy': 'Որակի վերահսկման գործընթաց',
            'ru': 'Процесс контроля качества'
        },
        'description': {
            'en': 'Our rigorous quality assurance checks at every production stage.',
            'hy': 'Մեր խիստ որակի վերահսկման ստուգումները արտադրության յուրաքանչյուր փուլում։',
            'ru': 'Наши строгие проверки качества на каждом этапе производства.'
        },
        'category': 'production',
        'duration': '1:00',
        'date': {
            'en': 'July 10, 2023',
            'hy': '2023թ. հուլիսի 10',
            'ru': '10 июля 2023 г.'
        }
    }
]

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
        MAIL_PORT = int(os.getenv('MAIL_PORT'))
        MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') == 'true'
        MAIL_USE_SSL = os.getenv('MAIL_USE_SSL') == 'true'
        MAIL_USERNAME = os.getenv('MAIL_USERNAME')
        MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
        MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
        return MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USE_SSL, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER

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

    def sort_products_by_priority(products, priority_order=['T', 'ATK', 'DP', 'L', 'B']):
        # Map each prefix to its priority index
        priority_map = {prefix.upper(): i for i, prefix in enumerate(priority_order)}

        def get_priority(product):
            code = str(product.get("code", "")).upper()
            for prefix in priority_order:
                if code.startswith(prefix.upper()):
                    return priority_map[prefix.upper()]
            return len(priority_order)  # Unknown prefix goes to the end

        # Sort by priority, then by code (for consistency)
        return sorted(products, key=lambda p: (get_priority(p), str(p.get("code", ""))))
