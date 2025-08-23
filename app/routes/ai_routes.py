from flask import Blueprint, request, jsonify
from app.services.ai_content_service import AIContentService

ai_bp = Blueprint('ai_bp', __name__, url_prefix='/api/ai')

ai_service = AIContentService()

@ai_bp.route('/generate_hashtags', methods=['POST'])
def generate_hashtags_route():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400

    text_content = data['text']
    num_hashtags = data.get('num_hashtags', 5) # Optional parameter

    hashtags = ai_service.generate_hashtags(text_content, num_hashtags)

    return jsonify({"hashtags": hashtags})
