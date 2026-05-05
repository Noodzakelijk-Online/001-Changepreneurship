"""
Integration tests — Phase 2 (Sprint 3)
Tests: S3-02 (Phase2IdeaService), S3-03 (AssumptionTracker), S3-05 (phase2 endpoints)
"""
import pytest
from datetime import datetime, timedelta

from src.models.assessment import db
from src.models.assessment import User, UserSession
from src.models.venture_record import VentureRecord, EvidenceItem
from src.services.phase2_idea_service import Phase2IdeaService
from src.services.assumption_tracker import (
    AssumptionTracker,
    ASSUMPTION_TYPE_AI_RESEARCH,
    ASSUMPTION_TYPE_VERIFIED_FACT,
    ASSUMPTION_TYPE_BEHAVIORAL_EVIDENCE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_user(db_session, username='tester_phase2', email='p2@test.com'):
    u = User(
        username=username,
        email=email,
        password_hash='x' * 60,
    )
    db_session.add(u)
    db_session.flush()
    return u


def make_session(db_session, user_id, token='tok-p2-001'):
    s = UserSession(
        user_id=user_id,
        session_token=token,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    db_session.add(s)
    db_session.flush()
    return s


def auth_header(token):
    return {'Authorization': f'Bearer {token}'}


# ---------------------------------------------------------------------------
# S3-02: Phase2IdeaService unit tests
# ---------------------------------------------------------------------------
class TestPhase2IdeaService:
    def setup_method(self):
        self.svc = Phase2IdeaService()

    def test_problem_undefined_blocks_hard(self):
        r = {'idea_description': 'An app', 'target_user_description': 'small businesses'}
        result = self.svc.evaluate_idea_clarity(r)
        assert result.idea_block_level == 4
        types = [b.type for b in result.blockers]
        assert 'PROBLEM_UNDEFINED' in types

    def test_everyone_target_blocks_hard(self):
        r = {
            'idea_description': 'An app',
            'problem_description': 'People lose track of tasks',
            'target_user_description': 'everyone who works',
        }
        result = self.svc.evaluate_idea_clarity(r)
        assert result.idea_block_level == 4
        types = [b.type for b in result.blockers]
        assert 'TARGET_TOO_BROAD' in types

    def test_clear_idea_no_blocks(self):
        r = {
            'idea_description': 'A task manager for solo freelancers',
            'problem_description': 'Freelancers lose 3h/week to manual invoicing',
            'target_user_description': 'solo freelancers in Europe with 3+ clients',
            'value_prop': 'Saves 3 hours per week by automating invoice generation',
            'first_use_case': 'Freelancer creates invoice in 30 seconds after project',
        }
        result = self.svc.evaluate_idea_clarity(r)
        assert result.idea_block_level < 4
        assert result.can_generate_cvc is True

    def test_cvc_generated_when_no_hard_block(self):
        r = {
            'idea_description': 'Project management for remote teams',
            'problem_description': 'Remote teams miss deadlines due to poor async coordination',
            'target_user_description': 'remote software teams of 5-15 people',
            'value_prop': 'Reduces missed deadlines by 60% through async check-ins',
        }
        result = self.svc.evaluate_idea_clarity(r)
        result = self.svc.generate_cvc_from_responses(r, result)
        assert result.cvc_generated is True
        assert result.problem_statement is not None
        assert result.target_user_hypothesis is not None
        assert result.value_proposition is not None
        assert len(result.assumptions) > 0

    def test_clarity_score_decreases_with_missing_fields(self):
        r_full = {
            'idea_description': 'App',
            'problem_description': 'Clear defined problem here',
            'target_user_description': 'freelancers',
            'value_prop': 'saves time',
            'first_use_case': 'creates report',
        }
        r_empty = {'idea_description': 'App'}
        result_full = self.svc.evaluate_idea_clarity(r_full)
        result_empty = self.svc.evaluate_idea_clarity(r_empty)
        assert result_full.clarity_score > result_empty.clarity_score

    def test_venture_type_inferred_nonprofit(self):
        r = {
            'idea_description': 'A nonprofit platform for charity donations',
            'problem_description': 'People cannot find local nonprofits',
            'target_user_description': 'donors in urban areas',
        }
        result = self.svc.evaluate_idea_clarity(r)
        assert result.venture_type_hint == 'NONPROFIT'

    def test_cvc_not_generated_on_hard_block(self):
        r = {'idea_description': 'Something', 'target_user_description': 'everyone'}
        result = self.svc.evaluate_idea_clarity(r)
        result = self.svc.generate_cvc_from_responses(r, result)
        assert result.cvc_generated is False


# ---------------------------------------------------------------------------
# S3-03: AssumptionTracker unit tests
# ---------------------------------------------------------------------------
class TestAssumptionTracker:
    def setup_method(self):
        self.tracker = AssumptionTracker()

    def test_create_assumption(self):
        a = self.tracker.create_assumption(
            venture_id=1,
            claim='Target user experiences this weekly',
            assumption_type=ASSUMPTION_TYPE_AI_RESEARCH,
            source='ai',
        )
        assert a.assumption_type == ASSUMPTION_TYPE_AI_RESEARCH
        assert not a.tested

    def test_ai_assumption_capped_at_ai_research(self):
        """CEO invariant: AI cannot produce VERIFIED_FACT"""
        a = self.tracker.create_assumption(
            venture_id=1,
            claim='Something is true',
            assumption_type=ASSUMPTION_TYPE_VERIFIED_FACT,
            source='ai',
        )
        assert a.assumption_type == ASSUMPTION_TYPE_AI_RESEARCH

    def test_mark_tested_upgrades_type(self):
        a = self.tracker.create_assumption(
            venture_id=1,
            claim='Hypothesis',
            assumption_type=ASSUMPTION_TYPE_AI_RESEARCH,
            source='ai',
        )
        a = self.tracker.mark_tested(
            a, 'Confirmed via 5 interviews', new_type=ASSUMPTION_TYPE_BEHAVIORAL_EVIDENCE,
        )
        assert a.tested is True
        assert a.assumption_type == ASSUMPTION_TYPE_BEHAVIORAL_EVIDENCE

    def test_summary_computes_pct(self):
        assumptions = [
            {'id': 'a1', 'tested': True, 'assumption_type': 'AI_RESEARCH'},
            {'id': 'a2', 'tested': False, 'assumption_type': 'USER_BELIEF'},
            {'id': 'a3', 'tested': False, 'assumption_type': 'AI_RESEARCH'},
        ]
        summary = self.tracker.compute_summary(assumptions, venture_id=1)
        assert summary.total == 3
        assert summary.tested == 1
        assert summary.untested == 2
        assert summary.tested_pct == pytest.approx(33.3, abs=0.2)

    def test_get_pending_validation(self):
        assumptions = [
            {'id': 'a1', 'tested': True},
            {'id': 'a2', 'tested': False},
        ]
        pending = self.tracker.get_pending_validation(assumptions)
        assert len(pending) == 1
        assert pending[0]['id'] == 'a2'

    def test_evidence_upgrades_assumption_type(self):
        a = self.tracker.create_assumption(
            venture_id=1, claim='Hypothesis', assumption_type=ASSUMPTION_TYPE_AI_RESEARCH, source='ai',
        )
        original_tier = a.confidence_tier
        a = self.tracker.update_with_evidence(a, 'INTERVIEW', 'DIRECT', 'User confirmed via zoom call')
        assert a.confidence_tier > original_tier

    def test_evidence_never_downgrades(self):
        a = self.tracker.create_assumption(
            venture_id=1, claim='Hypothesis',
            assumption_type=ASSUMPTION_TYPE_BEHAVIORAL_EVIDENCE,
            source='user',
        )
        original_tier = a.confidence_tier
        a = self.tracker.update_with_evidence(a, 'DESK', 'BELIEF', 'Weak belief')
        assert a.confidence_tier >= original_tier


# ---------------------------------------------------------------------------
# S3-05: Phase 2 endpoint integration tests
# ---------------------------------------------------------------------------
class TestPhase2Submit:
    def test_auth_required(self, client):
        resp = client.post('/api/v1/phase2/submit', json={'responses': {}})
        assert resp.status_code in (401, 403)

    def test_submit_with_hard_block_returns_200_no_cvc(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id, 'tok-p2-hb')
            db.session.commit()

        resp = client.post(
            '/api/v1/phase2/submit',
            json={'responses': {
                'idea_description': 'Some app',
                'target_user_description': 'everyone',
                'problem_description': '',
            }},
            headers=auth_header('tok-p2-hb'),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['can_generate_cvc'] is False
        assert data['cvc'] is None
        assert len(data['blockers']) > 0

    def test_submit_clear_idea_generates_cvc(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'tester_p2_clear', 'p2clear@test.com')
            make_session(db.session, u.id, 'tok-p2-clear')
            db.session.commit()

        resp = client.post(
            '/api/v1/phase2/submit',
            json={'responses': {
                'idea_description': 'Project management for remote teams',
                'problem_description': 'Remote teams miss deadlines from poor async comms',
                'target_user_description': 'remote software teams of 5-15 people',
                'value_prop': 'Reduces missed deadlines by 60%',
                'first_use_case': 'Team lead sets daily async check-in',
            }},
            headers=auth_header('tok-p2-clear'),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['can_generate_cvc'] is True
        assert data['cvc'] is not None
        assert data['venture_id'] is not None

    def test_submit_empty_responses_returns_400(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'tester_400', 'p2400@test.com')
            make_session(db.session, u.id, 'tok-p2-400')
            db.session.commit()

        resp = client.post(
            '/api/v1/phase2/submit',
            json={},
            headers=auth_header('tok-p2-400'),
        )
        assert resp.status_code == 400


class TestPhase2GetVenture:
    def test_no_venture_returns_null(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'noventure', 'nv@test.com')
            make_session(db.session, u.id, 'tok-nv')
            db.session.commit()

        resp = client.get('/api/v1/phase2/venture', headers=auth_header('tok-nv'))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['venture'] is None

    def test_venture_returned_after_submit(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'venture_getter', 'vg@test.com')
            make_session(db.session, u.id, 'tok-vg')
            db.session.commit()

        # Submit first
        client.post(
            '/api/v1/phase2/submit',
            json={'responses': {
                'idea_description': 'SaaS tool',
                'problem_description': 'Teams waste time on manual reporting',
                'target_user_description': 'operations managers in mid-size companies',
                'value_prop': 'Save 5 hours weekly on reports',
            }},
            headers=auth_header('tok-vg'),
        )

        resp = client.get('/api/v1/phase2/venture', headers=auth_header('tok-vg'))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['venture'] is not None
        assert 'assumption_summary' in data['venture']


class TestPhase2MarkAssumptionTested:
    def test_mark_tested(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'tester_mark', 'mark@test.com')
            make_session(db.session, u.id, 'tok-mark')
            v = VentureRecord(
                user_id=u.id, version=1, is_active=True,
                idea_raw='Test idea',
                assumptions=[{'id': 'a1', 'claim': 'Test assumption', 'tested': False}],
                status='DRAFT',
            )
            db.session.add(v)
            db.session.commit()
            vid = v.id

        resp = client.post(
            '/api/v1/phase2/assumptions/test',
            json={
                'venture_id': vid,
                'assumption_id': 'a1',
                'test_result': 'Confirmed via interviews',
            },
            headers=auth_header('tok-mark'),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['updated'] is True

    def test_missing_required_returns_400(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'tester_req', 'req@test.com')
            make_session(db.session, u.id, 'tok-req')
            db.session.commit()

        resp = client.post(
            '/api/v1/phase2/assumptions/test',
            json={'venture_id': 1},
            headers=auth_header('tok-req'),
        )
        assert resp.status_code == 400


class TestPhase2Evidence:
    def test_submit_evidence(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'tester_ev', 'ev@test.com')
            make_session(db.session, u.id, 'tok-ev')
            v = VentureRecord(
                user_id=u.id, version=1, is_active=True,
                idea_raw='Evidence venture', status='DRAFT',
            )
            db.session.add(v)
            db.session.commit()
            vid = v.id

        resp = client.post(
            '/api/v1/phase2/evidence',
            json={
                'venture_id': vid,
                'evidence_type': 'INTERVIEW',
                'strength': 'DIRECT',
                'description': 'Spoke with 5 target users who confirmed the problem',
            },
            headers=auth_header('tok-ev'),
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert 'evidence_id' in data

    def test_evidence_missing_description_returns_400(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'tester_ev2', 'ev2@test.com')
            make_session(db.session, u.id, 'tok-ev2')
            db.session.commit()

        resp = client.post(
            '/api/v1/phase2/evidence',
            json={'evidence_type': 'INTERVIEW'},
            headers=auth_header('tok-ev2'),
        )
        assert resp.status_code == 400
