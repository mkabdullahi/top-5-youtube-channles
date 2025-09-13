from flask import Blueprint, request, jsonify, current_app, url_for, session
from authlib.integrations.flask_client import OAuth
from flask_login import login_required, current_user
import os

oauth_bp = Blueprint('oauth', __name__)
oauth = OAuth()

# Initialize OAuth providers
oauth.register(
    name='youtube',
    client_id=os.getenv('YOUTUBE_CLIENT_ID'),
    client_secret=os.getenv('YOUTUBE_CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/youtube/v3/',
    client_kwargs={'scope': 'https://www.googleapis.com/auth/youtube.readonly'}
)

oauth.register(
    name='instagram',
    client_id=os.getenv('INSTAGRAM_CLIENT_ID'),
    client_secret=os.getenv('INSTAGRAM_CLIENT_SECRET'),
    access_token_url='https://api.instagram.com/oauth/access_token',
    access_token_params=None,
    authorize_url='https://api.instagram.com/oauth/authorize',
    authorize_params=None,
    api_base_url='https://graph.instagram.com/',
    client_kwargs={'scope': 'user_profile,user_media'}
)

@oauth_bp.route('/connect/<platform>')
@login_required
def connect_platform(platform):
    if platform not in ['youtube', 'instagram', 'tiktok']:
        return jsonify({'error': 'Invalid platform'}), 400
        
    # Store the platform name in session for the callback
    session['connecting_platform'] = platform
    
    # Get the appropriate OAuth provider
    provider = oauth.create_client(platform)
    if not provider:
        return jsonify({'error': 'Platform not configured'}), 400
        
    redirect_uri = url_for('oauth.authorize', _external=True)
    return provider.authorize_redirect(redirect_uri)

@oauth_bp.route('/authorize')
@login_required
def authorize():
    platform = session.get('connecting_platform')
    if not platform:
        return jsonify({'error': 'No platform specified'}), 400
        
    provider = oauth.create_client(platform)
    token = provider.authorize_access_token()
    
    # Store the token in user's platform connections
    current_user.platforms[platform] = {
        'access_token': token['access_token'],
        'connected_at': datetime.utcnow().isoformat()
    }
    
    # Update user in database
    current_app.mongo.db.users.update_one(
        {'_id': current_user.id},
        {'$set': {'platforms': current_user.platforms}}
    )
    
    return jsonify({
        'message': f'Successfully connected to {platform}',
        'platform': platform
    })