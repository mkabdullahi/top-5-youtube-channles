import os
import requests
from app.services.base import BasePlatformService
from app import mongo

class YouTubeService(BasePlatformService):
    def __init__(self, api_key=None, cache_ttl=3600):
        super().__init__(cache_ttl)
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.base_url = 'https://www.googleapis.com/youtube/v3'
        
    def get_top_influencers(self, category, limit=5):
        cache_key = self._get_cache_key(['youtube', category, limit])
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
            
        # API call implementation
        response = requests.get(
            f"{self.base_url}/search",
            params={
                'part': 'snippet',
                'type': 'channel',
                'q': category,
                'maxResults': limit,
                'key': self.api_key
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self._set_cached_data(cache_key, data)
            return data
            
        return None
        
    def get_metrics(self, channel_id):
        cache_key = self._get_cache_key(['youtube', 'metrics', channel_id])
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
            
        response = requests.get(
            f"{self.base_url}/channels",
            params={
                'part': 'statistics',
                'id': channel_id,
                'key': self.api_key
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self._set_cached_data(cache_key, data)
            return data
            
        return None