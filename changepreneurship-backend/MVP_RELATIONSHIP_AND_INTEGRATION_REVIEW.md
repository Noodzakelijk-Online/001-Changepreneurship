# MVP Relationship Review and Integration Backlog

This document records the review status of the MVP infrastructure branch after adding the readiness/action/mentor-source systems.

## Current status

The branch now includes:

- backend models for readiness, ventures, gates, actions, evidence, assumptions, cost estimates, spending caps, outcomes, professional review, and connection mode;
- route groups under `/api/mvp`, `/api/mvp/logic`, and `/api/mvp/mentor-sources`;
- a frontend test page at `/mvp-action-review`;
- a reviewed Alembic migration file attached to the current migration head;
- GitHub Actions checks for backend imports and frontend build.

## SQLAlchemy relationship review

### Good enough for this infrastructure pass

The MVP models use explicit foreign keys for:

- user ownership;
- venture ownership;
- action ownership;
- evidence-to-assumption links;
- action-to-permission policy;
- action-to-outcome;
- action-to-cost estimate;
- user/venture-level spending caps;
- user/venture-level professional review requirements.

The model layer is intentionally conservative: most relationships are one-directional or accessed through explicit queries rather than heavy automatic relationship chains.

This is acceptable for an MVP infrastructure pass because it reduces the risk of circular imports and accidental cascade behaviour.

### Items a developer should inspect before merge

1. **Cascade behaviour**
   - The new models mostly rely on foreign keys and explicit queries.
   - Before production use, decide whether deleting a user or venture should cascade-delete all evidence/actions/outcomes or whether records should be retained/anonymized for audit reasons.

2. **Audit and compliance retention**
   - `UserAction`, `ActionOutcome`, `DataConsentLog`, and `ProfessionalReviewRequirement` may need retention rules rather than normal deletion.
   - This should be decided before production GDPR/data-retention work.

3. **JSON text fields**
   - Several records use text-based JSON to stay compatible with SQLite and PostgreSQL.
   - Later, PostgreSQL `JSONB` could be used for better querying.

4. **Indexes**
   - The migration adds basic user/venture/action indexes.
   - Later, add indexes for frequently filtered fields such as `status`, `action_type`, `evidence_strength`, `gate_status`, and `outcome_status` if query volume grows.

5. **ExternalConnection tokens**
   - Token fields exist but real encryption is not implemented yet.
   - Do not store real OAuth tokens until encryption/key management is added and reviewed.

## Migration review

Migration file:

`migrations/versions/20260503_02_add_mvp_infrastructure_and_logic.py`

The migration is manually written and attached to:

`down_revision = 'add_resume_enrichment_fields'`

This matches the current latest migration head in `main` at the time of this branch.

Before merge/deploy, run:

```bash
cd changepreneurship-backend
flask db upgrade
flask db downgrade -1
flask db upgrade
```

The downgrade/upgrade loop matters because this migration creates many linked tables.

## Frontend review

New page:

`/mvp-action-review`

Purpose:

- run `/api/mvp/bootstrap-from-assessment`;
- show proposed action;
- approve latest action;
- mock-execute latest action;
- request mentor-source recommendations;
- create mentor-outreach action from a selected mentor platform.

This page is intentionally an internal/test page, not final UX.

## Real integration backlog

The mentor-source router now distinguishes manual sources, account-reference sources, and future integration candidates. The next real integration step should be handled platform-by-platform.

### Phase 1 — Account reference support

This is already structurally supported.

For each mentor platform, store:

- profile URL;
- username/email if user provides it;
- application URL;
- booking link;
- local chapter/contact;
- notes.

This allows Changepreneurship to route the user to the correct source even without API access.

### Phase 2 — Manual assisted execution

For platforms without APIs:

- prepare message;
- prepare account/application steps;
- ask user to copy/paste or manually submit;
- let user mark outcome;
- track follow-up.

This is the safest near-term approach.

### Phase 3 — API/OAuth research

Research each source separately:

- MicroMentor
- ADPList
- PushFar
- SCORE
- SBDC
- Futurpreneur Canada
- Digital Boost
- Startup India
- VC4A
- GrowthMentor

For each, document:

- public API available? yes/no/unknown;
- OAuth available? yes/no/unknown;
- terms permit automation? yes/no/unknown;
- login automation/RPA allowed? yes/no/unknown;
- safest execution mode.

### Phase 4 — First real integration candidate

Choose the first real integration based on:

- reliable API/OAuth availability;
- clear platform terms;
- relevance to the first target users;
- low risk of account bans;
- ability to create drafts rather than auto-send.

Email/Gmail may be safer than mentor-platform automation because the user controls the account and OAuth is mature. Mentor platforms can remain manual/account-reference initially.

## Recommended next developer task

Before attempting real external integrations, build one polished internal flow:

1. User completes assessment.
2. User opens `/mvp-action-review`.
3. System bootstraps readiness profile.
4. System recommends mentor route.
5. User chooses a mentor source.
6. System creates mentor-outreach action.
7. User approves.
8. System mock-executes or marks manual execution.
9. User records outcome.

This proves the MVP action loop without risky external automation.
