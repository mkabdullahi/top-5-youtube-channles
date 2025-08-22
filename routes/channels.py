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
        channels = get_top_5_channels_by_category(category)
        return jsonify({
            "category": category,
            "channels": channels
        })
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except RuntimeError as re:
        # Could be API failure or quota limit
        msg = str(re)
        status = 502
        if 'quota' in msg.lower():
            status = 429
        return jsonify({"error": "YouTube API error", "details": msg}), status
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@channels_bp.route('/view/<category>')
def view_channels(category):
    # Render a simple HTML page with the top channels
    try:
        channels = get_top_5_channels_by_category(category)
    except Exception:
        channels = []
    return render_template('channels.html', category=category, channels=channels)
