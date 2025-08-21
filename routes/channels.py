from flask import Blueprint, jsonify
from data.channels_data import generate_dummy_data

channels_bp = Blueprint('channels', __name__)

@channels_bp.route('/channels/<category>')
def get_channels(category):
    return jsonify({
        "category": category,
        "channels": generate_dummy_data(category)
    })
