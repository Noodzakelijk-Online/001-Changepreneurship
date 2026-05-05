# MVP Infrastructure Testing Guide

This branch adds a backend-only infrastructure pass for the Changepreneurship MVP direction.

It does not build the full MVP. It creates the first backend primitives for:

- structured readiness profiles;
- Maslow/stability-oriented routing;
- phase gates;
- consent logging;
- external connection placeholders;
- trusted action proposals;
- action approval/edit/reject/cancel/mock-execution;
- action audit logs.

## Important migration note

The model code is included in `src/models/mvp_infrastructure.py`.

Before testing against PostgreSQL, generate or review the Alembic migration locally:

```bash
cd changepreneurship-backend
flask db migrate -m "add MVP readiness and action infrastructure"
flask db upgrade
```

The migration should create these tables:

- `venture`
- `founder_readiness_profile`
- `phase_gate`
- `user_action`
- `external_connection`
- `data_consent_log`

## Route prefix

All routes are registered under:

```text
/api/mvp
```

A valid session token is required, using the same authentication style as the existing backend.

## Basic manual test flow

### 1. Create a venture

```bash
curl -X POST http://localhost:5000/api/mvp/ventures \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Venture","venture_type":"software","stage":"self_discovery"}'
```

### 2. Create a readiness profile

```bash
curl -X POST http://localhost:5000/api/mvp/readiness-profile \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "venture_id": 1,
    "survival_risk_indicator": "low",
    "risk_level": "medium",
    "route_confidence": "medium",
    "dimensions": {
      "financial_readiness": {"status":"adequate","confidence":"medium","evidence_note":"Basic runway exists","blocker_flag":false},
      "time_capacity": {"status":"adequate","confidence":"medium","evidence_note":"User has weekly time","blocker_flag":false},
      "personal_readiness": {"status":"adequate","confidence":"medium","evidence_note":"No critical personal blocker detected","blocker_flag":false},
      "founder_idea_fit": {"status":"adequate","confidence":"medium","evidence_note":"Idea roughly fits founder background","blocker_flag":false},
      "evidence_discipline": {"status":"weak","confidence":"medium","evidence_note":"Needs real-world validation","blocker_flag":false},
      "support_network": {"status":"weak","confidence":"medium","evidence_note":"Mentor support missing","blocker_flag":false}
    }
  }'
```

### 3. Ask the rule engine for the next step and create an action

```bash
curl -X POST http://localhost:5000/api/mvp/decide-next-step \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"venture_id":1,"create_action":true}'
```

Expected result: a typed decision and a proposed `UserAction`.

### 4. Approve the action

```bash
curl -X POST http://localhost:5000/api/mvp/actions/1/approve \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 5. Mock-execute the approved action

```bash
curl -X POST http://localhost:5000/api/mvp/actions/1/execute-mock \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"result":{"result":"mock completed for MVP infrastructure test"}}'
```

### 6. Inspect action history

```bash
curl http://localhost:5000/api/mvp/actions \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

The action should include an audit log showing proposal, approval, execution, and completion.

## What this branch intentionally does not do yet

- No real MicroMentor integration.
- No real Gmail/LinkedIn integration.
- No production OAuth token encryption implementation.
- No frontend review screen yet.
- No Venture Credits billing yet.
- No full 16-type founder classifier yet.
- No full 21-route decision engine yet.

## Correct next development step

After this backend pass is reviewed, the next useful step is a small frontend page:

```text
Recommended Action Review
- show proposed action
- show risk/cost/why
- approve/edit/reject/cancel
- mock execute
- show audit log
```

That creates the visible bridge from assessment platform to trusted action platform.
