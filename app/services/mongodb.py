from pymongo import MongoClient
from config.settings import Config

class MongoDB:
    _client = None
    _db = None

    @classmethod
    def initialize(cls):
        cls._client = MongoClient(Config.MONGODB_URI)
        cls._db = cls._client[Config.MONGODB_NAME]

    @classmethod
    def get_db(cls):
        if cls._db is None:
            cls.initialize()
        return cls._db

    @classmethod
    def close(cls):
        if cls._client:
            cls._client.close()
