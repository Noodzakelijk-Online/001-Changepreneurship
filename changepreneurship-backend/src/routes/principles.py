"""
Principles API Routes
"""
from flask import Blueprint, request, jsonify
from src.utils.redis_client import get_cached_json, cache_json
from src.services.principles_service import PrinciplesService

principles_bp = Blueprint('principles', __name__)
principles_service = PrinciplesService()

@principles_bp.route('/principles', methods=['GET'])
def get_principles():
    """
    Get principles filtered by category, stage, or search query
    Query parameters:
    - category: filter by category
    - stage: filter by business stage
    - limit: maximum number of results (default 5)
    - search: search in title and summary
    """
    try:
        category = request.args.get('category')
        stage = request.args.get('stage')
        limit = int(request.args.get('limit', 5))
        search = request.args.get('search')

        # Validate limit
        if limit < 1 or limit > 50:
            limit = 5

        cache_key_parts = []
        if search:
            cache_key_parts.append(f"search={search}")
        if category:
            cache_key_parts.append(f"cat={category}")
        if stage:
            cache_key_parts.append(f"stage={stage}")
        cache_key_parts.append(f"limit={limit}")
        cache_key = "principles:" + ("|".join(cache_key_parts) if cache_key_parts else "all")

        # Attempt cache lookup only for simple GET (avoid caching if search present with very short term?)
        cached = get_cached_json(cache_key)
        if cached is not None:
            return jsonify({'success': True, 'data': cached, 'count': len(cached), 'cached': True})

        # Compute fresh data
        if search:
            principles = principles_service.search_principles(search, limit)
        elif category or stage:
            principles = principles_service.get_principles_by_category_and_stage(
                category=category,
                stage=stage,
                limit=limit
            )
        else:
            all_principles = principles_service.get_all_principles()
            principles = all_principles[:limit]

        # Cache result (short TTL for search results, longer for static queries)
        try:
            ttl = 60 if search else 300  # 1 min for search variants, 5 min for others
            cache_json(cache_key, principles, ttl_seconds=ttl)
        except Exception:
            pass

        return jsonify({
            'success': True,
            'data': principles,
            'count': len(principles),
            'cached': False
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@principles_bp.route('/principles/<int:principle_id>', methods=['GET'])
def get_principle_by_id(principle_id):
    """Get a specific principle by ID"""
    try:
        principle = principles_service.get_principle_by_id(principle_id)

        if principle:
            return jsonify({
                'success': True,
                'data': principle
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Principle not found'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@principles_bp.route('/principles/categories', methods=['GET'])
def get_categories():
    """Get all available categories"""
    try:
        categories = principles_service.get_categories()
        return jsonify({
            'success': True,
            'data': categories
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@principles_bp.route('/principles/stages', methods=['GET'])
def get_stages():
    """Get all available business stages"""
    try:
        stages = principles_service.get_stages()
        return jsonify({
            'success': True,
            'data': stages
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@principles_bp.route('/principles/recommendations', methods=['POST'])
def get_recommendations():
    """
    Get personalized principle recommendations based on assessment results
    Expected JSON body:
    {
        "user_stage": "early_stage",
        "focus_areas": ["marketing", "product_development"],
        "limit": 5
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        user_stage = data.get('user_stage')
        focus_areas = data.get('focus_areas', [])
        limit = data.get('limit', 5)

        # Validate limit
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 5
        if limit < 1 or limit > 50:
            limit = 5

        recommendations = principles_service.get_recommendations(
            user_stage=user_stage,
            focus_areas=focus_areas,
            limit=limit,
        )

        return jsonify({
            'success': True,
            'data': recommendations,
            'count': len(recommendations)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
