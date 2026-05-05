from run_dev import app
from src.models.assessment import db, Assessment
from sqlalchemy import text

with app.app_context():
    r = db.session.execute(text("SELECT id, username, email FROM \"user\" WHERE username = 'alex_foundr'")).fetchone()
    if r:
        uid = r.id
        print("user_id=%d username=%s email=%s" % (uid, r.username, r.email))
        sess = db.session.execute(text("SELECT session_token, expires_at FROM user_session WHERE user_id = %d ORDER BY created_at DESC LIMIT 1" % uid)).fetchone()
        if sess:
            print("token=%s expires=%s" % (sess.session_token[:50], sess.expires_at))
        else:
            print("NO SESSION")
        rows = db.session.execute(text("SELECT phase_id, is_completed, progress_percentage FROM assessment WHERE user_id = %d" % uid)).fetchall()
        for row in rows:
            print("  phase=%s completed=%s progress=%.1f" % (row.phase_id, row.is_completed, row.progress_percentage or 0))
    else:
        print("NOT FOUND")
