from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.models.influencer import Influencer
from app.models.category import Category
from app.services.unified_search import UnifiedSearchService

influencer_bp = Blueprint('influencer', __name__)
unified_search = UnifiedSearchService()

@influencer_bp.route('/top/<category>', methods=['GET'])
@login_required
def get_top_influencers(category):
    platform = request.args.get('platform')  # Optional platform filter
    limit = int(request.args.get('limit', 5))
    
    # Search across all platforms or specific platform
    results = unified_search.search_all_platforms(category, limit)
    
    # Filter by platform if specified
    if platform:
        results = [r for r in results if r['platform'] == platform]
        
    # Save results to database
    for result in results:
        influencer = Influencer(
            platform=result['platform'],
            platform_id=result['id'],
            name=result['name'],
            category=category,
            metrics=result.get('metrics', {})
        )
        influencer.save()
        
    return jsonify(results)

@influencer_bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    categories = Category.get_all()
    return jsonify(categories)