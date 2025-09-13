from app import mongo
from datetime import datetime

class Influencer:
    def __init__(self, platform, platform_id, name, category, metrics=None):
        self.platform = platform
        self.platform_id = platform_id
        self.name = name
        self.category = category
        self.metrics = metrics or {}
        self.last_updated = datetime.utcnow()
    
    def save(self):
        return mongo.db.influencers.insert_one({
            'platform': self.platform,
            'platform_id': self.platform_id,
            'name': self.name,
            'category': self.category,
            'metrics': self.metrics,
            'last_updated': self.last_updated
        })
    
    @staticmethod
    def find_by_category(category, limit=5):
        return list(mongo.db.influencers.find(
            {'category': category},
            {'_id': 0}
        ).limit(limit))
    
    @staticmethod
    def find_by_platform_id(platform, platform_id):
        return mongo.db.influencers.find_one({
            'platform': platform,
            'platform_id': platform_id
        }, {'_id': 0})