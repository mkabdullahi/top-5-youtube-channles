from redis import Redis
from config.settings import Config

redis_client = Redis.from_url(Config.REDIS_URL)
