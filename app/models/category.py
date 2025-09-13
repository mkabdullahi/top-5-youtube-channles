from app import mongo
from datetime import datetime

class Category:
    def __init__(self, name, platform_tags=None):
        self.name = name
        self.platform_tags = platform_tags or {}
    
    def save(self):
        return mongo.db.categories.insert_one({
            'name': self.name,
            'platform_tags': self.platform_tags,
            'created_at': datetime.utcnow()
        })
    
    @staticmethod
    def get_all():
        return list(mongo.db.categories.find({}, {'_id': 0}))
    
    @staticmethod
    def find_by_name(name):
        return mongo.db.categories.find_one({
            'name': name
        }, {'_id': 0})