from celery import shared_task
from app import mongo, redis_client
from app.services.unified_search import UnifiedSearchService
import json
from datetime import datetime, timedelta

@shared_task
def update_influencer_data():
    """
    Background task to update influencer data
    """
    unified_search = UnifiedSearchService()
    categories = list(mongo.db.categories.find({}, {'name': 1}))
    
    for category in categories:
        try:
            # Get fresh data from platforms
            results = unified_search.search_all_platforms(category['name'])
            
            # Update database
            for result in results:
                mongo.db.influencers.update_one(
                    {
                        'platform': result['platform'],
                        'platform_id': result['id']
                    },
                    {
                        '$set': {
                            'name': result['name'],
                            'metrics': result['metrics'],
                            'last_updated': datetime.utcnow()
                        }
                    },
                    upsert=True
                )
                
        except Exception as e:
            print(f"Error updating {category['name']}: {str(e)}")
            
@shared_task
def cleanup_cache():
    """
    Remove expired cache entries
    """
    for key in redis_client.scan_iter("*"):
        try:
            # Check if TTL is expired
            if redis_client.ttl(key) <= 0:
                redis_client.delete(key)
        except Exception as e:
            print(f"Error cleaning up cache key {key}: {str(e)}")
            
class DataRefreshService:
    @staticmethod
    def schedule_updates():
        """
        Schedule periodic data updates
        """
        # Update influencer data every 6 hours
        update_influencer_data.apply_async(
            countdown=21600,  # 6 hours
            expires=25200     # 7 hours
        )
        
        # Clean cache every day
        cleanup_cache.apply_async(
            countdown=86400,  # 24 hours
            expires=90000     # 25 hours
        )