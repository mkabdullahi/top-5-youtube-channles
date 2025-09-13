from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.api.influencer import influencer_bp

api_bp = Blueprint('api', __name__)

# Register the influencer blueprint
api_bp.register_blueprint(influencer_bp, url_prefix='/influencers')

@api_bp.route('/platforms', methods=['GET'])
@login_required
def get_platforms():
    return jsonify({
        'connected_platforms': current_user.platforms
    })

@api_bp.route('/preferences', methods=['GET'])
@login_required
def get_preferences():
    return jsonify({
        'preferences': current_user.preferences
    })