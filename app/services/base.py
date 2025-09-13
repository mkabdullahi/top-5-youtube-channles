from abc import ABC, abstractmethod
from app.services.redis_client import redis_client
import json

class BasePlatformService(ABC):
    def __init__(self, cache_ttl=3600):
        self.cache_ttl = cache_ttl
        
    @abstractmethod
    def get_top_influencers(self, category, limit=5):
        pass
        
    @abstractmethod
    def get_metrics(self, influencer_id):
        pass
        
    def _get_cache_key(self, key_parts):
        return ':'.join(map(str, key_parts))
        
    def _get_cached_data(self, key):
        data = redis_client.get(key)
        return json.loads(data) if data else None
        
    def _set_cached_data(self, key, data):
        redis_client.setex(
            key,
            self.cache_ttl,
            json.dumps(data)
        )
