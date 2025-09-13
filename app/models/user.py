from app import mongo
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, email, password, preferences=None, platforms=None):
        self.email = email
        self.password = password
        self.preferences = preferences or {}
        self.platforms = platforms or {}
        
    def save(self):
        return mongo.db.users.insert_one({
            'email': self.email,
            'password': self.password,
            'preferences': self.preferences,
            'platforms': self.platforms
        })
        
    @staticmethod
    def find_by_email(email):
        user_data = mongo.db.users.find_one({'email': email})
        if user_data:
            return User(
                email=user_data['email'],
                password=user_data['password'],
                preferences=user_data.get('preferences', {}),
                platforms=user_data.get('platforms', {})
            )
        return None