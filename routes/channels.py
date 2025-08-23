from flask import Blueprint, jsonify, request
from data.channels_data import get_top_5_channels_by_category
from flask import render_template

channels_bp = Blueprint('channels', __name__)


@channels_bp.route('/channels/<category>')
def get_channels(category):
    # Validate category
    if not category or category.strip() == "":
        return jsonify({"error": "Category is required"}), 400

    try:
        channels, error = get_top_5_channels_by_category(category)
        if error:
            # Map simple errors to HTTP status
            status = 400 if 'required' in error.lower() else 502
            if 'quota' in (error or '').lower():
                status = 429
            return jsonify({"error": error}), status
        return jsonify({
            "category": category,
            "channels": channels
        })
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@channels_bp.route('/view/<category>')
def view_channels(category):
    # Render a simple HTML page with the top channels
    channels, error = get_top_5_channels_by_category(category)
    return render_template('channels.html', category=category, channels=channels, error=error)
