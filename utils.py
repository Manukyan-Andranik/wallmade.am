import os
import json
from bson import json_util

def load_env():
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    DEFAULT_INSTRUCTOR_PHOTO = os.getenv('DEFAULT_INSTRUCTOR_PHOTO')
    return MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER, DEFAULT_INSTRUCTOR_PHOTO

def export_collections_to_json(get_collections, output_dir="mongo_exports"):
    """Export each MongoDB collection to a separate JSON file with UTF-8 encoding"""
    os.makedirs(output_dir, exist_ok=True)
    collections = get_collections()

    for name, collection in collections.items():
        data = list(collection.find())
        with open(os.path.join(output_dir, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                default=json_util.default,
                ensure_ascii=False,  # ⬅️ Important for readable Armenian/Russian
                indent=2
            )

    print(f"Exported {len(collections)} collections to '{output_dir}/'")