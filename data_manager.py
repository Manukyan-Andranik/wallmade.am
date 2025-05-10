import json
from bson import json_util
from bson.objectid import ObjectId

from config import Config

class DataManager:
    def __init__(self):
        pass
        
    def get_collection_from_json(filename):
        full_filename = f"mongo_exports/{filename}.json"
        """Read a JSON file and return the collection data"""
        with open(full_filename, "r", encoding="utf-8") as f:
            data = json.load(f, object_hook=json_util.object_hook)

            if filename == "products":
                data = Config.sort_products_by_priority(data)
            
            return data

    def get_item_from_json_by_id(filename, object_id):
        """Fetch a single document from a JSON file by ObjectId"""
        full_filename = f"mongo_exports/{filename}.json"
        with open(full_filename, "r", encoding="utf-8") as f:
            data = json.load(f, object_hook=json_util.object_hook)
        
        for item in data:
            if str(item.get('_id')) == str(ObjectId(object_id)):
                return item
        return None

    def delete_item_from_json_by_id(filename, object_id):
        """Delete a single document from a JSON file by ObjectId"""
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f, object_hook=json_util.object_hook)

        new_data = [item for item in data if str(item.get("_id")) != str(ObjectId(object_id))]

        if len(new_data) == len(data):
            return False  # Nothing deleted

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(new_data, f, default=json_util.default, indent=2, ensure_ascii=False)

        return True  # Deletion successful
