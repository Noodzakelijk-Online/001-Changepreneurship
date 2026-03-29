from datetime import datetime

from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename

from src.models.assessment import db, EntrepreneurProfile
from src.services.resume_analysis_service import ResumeAnalysisService
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter


data_import_bp = Blueprint('data_import', __name__)
resume_analysis_service = ResumeAnalysisService()

ALLOWED_RESUME_EXTENSIONS = {'.pdf', '.txt'}


def _get_or_create_profile(user_id):
    profile = EntrepreneurProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = EntrepreneurProfile(user_id=user_id)
        db.session.add(profile)
    return profile


@data_import_bp.route('/resume', methods=['POST'])
@limiter.limit('10 per hour')
def upload_resume():
    user, _, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({'error': 'Resume file is required'}), 400

    filename = secure_filename(file.filename)
    ext = f".{filename.rsplit('.', 1)[-1].lower()}" if '.' in filename else ''
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        return jsonify({'error': 'Unsupported file type. Upload a PDF or TXT file.'}), 400

    try:
        text = resume_analysis_service.extract_text(file)
        if not text or len(text.strip()) < 80:
            return jsonify({'error': 'Could not extract enough text from the uploaded resume'}), 400

        result = resume_analysis_service.analyze(text)

        profile = _get_or_create_profile(user.id)
        profile.set_json_field('resume_data', result['parsed_data'])
        profile.set_json_field('resume_analysis', result['analysis'])
        profile.resume_uploaded_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Resume analyzed successfully',
            'parsed_data': result['parsed_data'],
            'analysis': result['analysis'],
            'suggested_profile': result['suggested_profile'],
            'profile': profile.to_dict(),
        }), 200
    except Exception as exc:
        current_app.logger.error(f'Resume import error: {exc}')
        return jsonify({'error': 'Failed to analyze resume'}), 500