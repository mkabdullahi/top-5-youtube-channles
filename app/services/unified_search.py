from app.services.youtube import YouTubeService
from app.services.instagram import InstagramService
from app.services.tiktok import TikTokService
from app.services.redis_client import redis_client
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

class UnifiedSearchService:
    def __init__(self):
        self.youtube = YouTubeService()
        self.instagram = InstagramService()
        self.tiktok = TikTokService()
        self.cache_ttl = 3600  # 1 hour
        
    def search_all_platforms(self, category, limit=5):
        """
        Search across all platforms and return unified results
        """
        cache_key = f'unified_search:{category}:{limit}'
        cached_results = self._get_cached_results(cache_key)
        
        if cached_results:
            return cached_results
            
        # Parallel search across platforms
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                'youtube': executor.submit(self.youtube.get_top_influencers, category, limit),
                'instagram': executor.submit(self.instagram.get_top_influencers, category, limit),
                'tiktok': executor.submit(self.tiktok.get_top_influencers, category, limit)
            }
            
        # Collect and normalize results
        results = {}
        for platform, future in futures.items():
            try:
                platform_results = future.result()
                if platform_results:
                    results[platform] = self._normalize_results(platform, platform_results)
            except Exception as e:
                print(f"Error fetching {platform} results: {str(e)}")
                
        # Rank and merge results
        merged_results = self._merge_and_rank_results(results, limit)
        
        # Cache the results
        self._cache_results(cache_key, merged_results)
        
        return merged_results
        
    def _normalize_results(self, platform, results):
        """
        Normalize platform-specific results to a common format
        """
        normalized = []
        
        if platform == 'youtube':
            for item in results.get('items', []):
                normalized.append({
                    'platform': 'youtube',
                    'id': item['id']['channelId'],
                    'name': item['snippet']['title'],
                    'description': item['snippet'].get('description', ''),
                    'metrics': self.youtube.get_metrics(item['id']['channelId']) or {}
                })
                
        elif platform == 'instagram':
            # Instagram normalization logic
            pass
            
        elif platform == 'tiktok':
            # TikTok normalization logic
            pass
            
        return normalized
        
    def _merge_and_rank_results(self, results, limit):
        """
        Merge results from all platforms and rank them by engagement
        """
        all_results = []
        
        # Combine all platform results
        for platform_results in results.values():
            all_results.extend(platform_results)
            
        # Sort by engagement score
        ranked_results = sorted(
            all_results,
            key=self._calculate_engagement_score,
            reverse=True
        )
        
        return ranked_results[:limit]
        
    def _calculate_engagement_score(self, influencer):
        """
        Calculate a normalized engagement score across platforms
        """
        metrics = influencer.get('metrics', {})
        
        if influencer['platform'] == 'youtube':
            subscribers = int(metrics.get('subscriberCount', 0))
            views = int(metrics.get('viewCount', 0))
            return (subscribers * 0.7) + (views * 0.3)
            
        # Add similar calculations for other platforms
        return 0
        
    def _get_cached_results(self, key):
        data = redis_client.get(key)
        return json.loads(data) if data else None
        
    def _cache_results(self, key, results):
        redis_client.setex(
            key,
            self.cache_ttl,
            json.dumps(results)
        )
