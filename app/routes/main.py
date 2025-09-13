from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.category import Category
from app import mongo

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    categories = Category.get_all()
    return render_template('dashboard.html', categories=categories)

@main_bp.route('/categories')
@login_required
def categories():
    categories = Category.get_all()
    return render_template('categories.html', categories=categories)

@main_bp.route('/preferences', methods=['POST'])
@login_required
def update_preferences():
    categories = request.form.getlist('categories[]')
    
    # Update user preferences in database
    mongo.db.users.update_one(
        {'_id': current_user.id},
        {'$set': {'preferences.categories': categories}}
    )
    
    flash('Preferences updated successfully', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/bookmark/<platform>/<influencer_id>', methods=['POST'])
@login_required
def bookmark_influencer(platform, influencer_id):
    # Add influencer to user's bookmarks
    bookmarks = current_user.preferences.get('bookmarks', [])
    bookmark_data = {
        'platform': platform,
        'influencer_id': influencer_id
    }
    
    if bookmark_data not in bookmarks:
        bookmarks.append(bookmark_data)
        mongo.db.users.update_one(
            {'_id': current_user.id},
            {'$set': {'preferences.bookmarks': bookmarks}}
        )
        return jsonify({'message': 'Influencer bookmarked'}), 200
        
    return jsonify({'message': 'Already bookmarked'}), 400