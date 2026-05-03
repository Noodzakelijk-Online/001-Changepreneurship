# MVP Document Requirements Map

This file maps codable requirements from the Changepreneurship business requirements document to the current MVP infrastructure branch.

The current branch already adds the first backend foundation:

- `Venture`
- `FounderReadinessProfile`
- `PhaseGate`
- `UserAction`
- `ExternalConnection`
- `DataConsentLog`
- `PathDecisionEngine`
- `ActionEngine`
- `/api/mvp/bootstrap-from-assessment`

The next work should not create a separate second system. It should connect the document requirements into these models and services.

---

## 1. Blocker priority order

Document requirement:
The platform should resolve blockers in this order:

1. Legal, ethical, safety, and regulatory risks
2. Personal crisis, burnout, or immediate harm risk
3. Financial survival and debt pressure
4. Data contradictions or unreliable answers
5. Idea clarity
6. Market demand and evidence quality
7. Business model and financial logic
8. Feasibility and operational readiness
9. Mentor/support gaps
10. Communication and positioning readiness
11. Acceleration or normal progression

Implementation target:

- Add a `BLOCKER_PRIORITY_ORDER` constant to `PathDecisionEngine`.
- Replace ad-hoc route priority with explicit priority evaluation.
- Ensure a lower-priority issue cannot override a higher-priority hard blocker.
- Add unit tests for priority conflicts.

Acceptance test:
If financial survival is critical and market evidence is also weak, the engine routes to financial stabilization first.

---

## 2. Standard blocking message structure

Document requirement:
Every block should explain:

1. blocked action
2. reason
3. risk
4. what remains allowed
5. unlock condition

Implementation target:

- Add these fields to the `PathDecision` dataclass:
  - `blocked_action`
  - `risk_explanation`
  - `allowed_actions`
  - `unlock_condition`
  - `user_facing_message`
- Generate a standard message from those fields.
- Store these values in `PhaseGate` where applicable.

Acceptance test:
A market-evidence blocker returns a complete explanation instead of only a generic route label.

---

## 3. Evidence labels

Document requirement:
The platform must distinguish assumptions from evidence and must not let AI turn assumptions into validated claims.

Implementation target:

Create a lightweight `EvidenceRecord` model:

- `id`
- `user_id`
- `venture_id`
- `evidence_type`
- `source`
- `claim`
- `evidence_strength`: assumption / weak_signal / partial_validation / strong_validation / verified_fact
- `confidence`
- `created_at`

Connect it to:

- readiness profile
- path decision engine
- market validation blockers
- future document generation

Acceptance test:
A user without `partial_validation` or stronger evidence cannot unlock product-building or investor-ready claims.

---

## 4. Assumption map

Document requirement:
The platform should challenge weak assumptions and require validation before serious execution.

Implementation target:

Create `AssumptionRecord`:

- `id`
- `user_id`
- `venture_id`
- `assumption_text`
- `category`
- `status`: untested / testing / validated / invalidated / replaced
- `risk_level`
- `linked_evidence_id`
- `created_at`
- `updated_at`

Acceptance test:
The platform can create a validation action from an untested high-risk assumption.

---

## 5. User type routing state

Document requirement:
User types A-P should be dynamic routing states, not permanent labels.

Implementation target:

Add a `FounderTypeClassifier` service that returns:

- `founder_type`
- `confidence`
- `reason`
- `recommended_pacing`
- `language_style`
- `risk_sensitivity`

Start with rule-based classification from existing readiness/assessment data.

First supported types:

- Type A: Aspiring First-Time Founder
- Type B: Career Switcher
- Type E: Side-Hustler With Traction
- Type H: Impact-Driven Founder
- Type I: Underprepared but Highly Motivated User
- Type L: Digital Product / Software Founder
- Type P: Non-Idea Entrepreneur

Acceptance test:
A user with no idea but strong entrepreneurship intent is routed to Type P and self-discovery/opportunity discovery, not market validation.

---

## 6. User fit and exclusion classifier

Document requirement:
The platform should distinguish:

- permanent non-fit
- temporary non-fit
- conditional fit
- hard exclusion

Implementation target:

Create `UserFitAssessment` model or service output:

- `fit_category`
- `reason`
- `allowed_mode`
- `blocked_actions`
- `redirect_route`
- `unlock_condition`

Connect to `PathDecisionEngine` before normal venture routing.

Acceptance test:
A user seeking get-rich-quick or harmful/deceptive venture support is not routed into normal venture-building.

---

## 7. Permission levels for external actions

Document requirement:
The platform must distinguish drafting, recommending, preparing, sending, applying, editing, submitting, and following up.

Implementation target:

Add explicit permission/action modes to `UserAction`:

- `permission_scope`
- `execution_mode`: manual / draft_only / assisted / external_execute / follow_up
- `requires_external_effect`: boolean
- `requires_explicit_approval`: boolean

Update `ActionEngine` so actions with external effects cannot execute unless approved.

Acceptance test:
A send/apply/submit action cannot be mock-executed unless status is `approved`.

---

## 8. Outcome tracking

Document requirement:
The MVP must track what happened after an action: sent, replied, stuck, succeeded, failed, next follow-up.

Implementation target:

Create `ActionOutcome` or extend `UserAction` with structured outcome fields:

- `outcome_status`: pending / sent / replied / no_reply / failed / completed / follow_up_needed
- `outcome_summary`
- `next_follow_up_at`
- `next_recommended_action_type`

Acceptance test:
After mock execution, the action can be updated to `follow_up_needed` with a next follow-up date.

---

## 9. Benchmark event tracking

Document requirement:
The platform should learn from outcomes and benchmark user journeys.

Implementation target:

Create `BenchmarkEvent`:

- `user_id`
- `venture_id`
- `event_type`
- `route`
- `founder_type`
- `phase_id`
- `action_type`
- `outcome_status`
- `metadata`
- `created_at`

This should be internal analytics, not user-facing first.

Acceptance test:
When an action is completed, a benchmark event is recorded.

---

## 10. Resource-metered cost estimate

Document requirement:
Meaningful paid actions should show cost before execution. Internal formula: actual resource cost x 2.5.

Implementation target:

Create `CostEstimate`:

- `user_id`
- `venture_id`
- `action_id`
- `estimated_direct_cost`
- `estimated_billed_price`
- `actual_direct_cost`
- `actual_billed_price`
- `pricing_multiplier`: default 2.5
- `pricing_basis`

Add a cost-estimation service with the fixed formula.

Acceptance test:
An action with estimated direct cost 1.00 returns estimated billed price 2.50.

---

## 11. User spending caps

Document requirement:
The user should remain in control and approve meaningful paid work.

Implementation target:

Create `SpendingCap`:

- `user_id`
- `venture_id`
- `cap_type`: per_action / daily / weekly / monthly
- `amount`
- `currency`
- `requires_approval_above_amount`
- `created_at`

Connect to `ActionEngine` before execution.

Acceptance test:
An action estimate above the user's per-action cap cannot execute without explicit approval.

---

## 12. AI boundary rules

Document requirement:
Fixed rules define the rails; AI drives within the rails; the user approves high-impact actions.

Implementation target:

Create `AIBoundaryPolicy` constants/service:

- no fabricated evidence
- no validated claims without evidence
- no hard-blocker override
- no external action without consent
- no professional advice replacement
- no spending without approval

Use this as a guard before AI-generated content is accepted into `UserAction` or external documents.

Acceptance test:
If a generated action claims validation without evidence, it is rejected or downgraded to assumption language.

---

## 13. Professional review routing

Document requirement:
The platform must refer to professionals where licensed judgment is required.

Implementation target:

Create `ProfessionalReviewRequirement`:

- `category`: legal / tax / accounting / medical / financial / regulated / mental_health
- `trigger_reason`
- `required_before_action_type`
- `status`: required / satisfied / waived_by_admin
- `professional_notes`

Acceptance test:
A legal/regulatory blocker prevents external submission until professional review status is satisfied.

---

## 14. Manual vs connected mode

Document requirement:
Account connection is optional but strongly encouraged; manual mode should still exist.

Implementation target:

Add user/venture-level mode:

- `manual_mode`
- `partially_connected_mode`
- `fully_connected_mode`

At minimum, expose this in the action proposal response so the UI can explain what is manual and what is connected.

Acceptance test:
If no external connection exists, the platform proposes manual or draft-only execution rather than failing.

---

## Recommended coding order from this map

1. Blocker priority order and blocking message fields
2. EvidenceRecord and AssumptionRecord
3. FounderTypeClassifier
4. UserFitAssessment
5. Permission/action modes
6. ActionOutcome tracking
7. BenchmarkEvent
8. CostEstimate and SpendingCap
9. AIBoundaryPolicy
10. ProfessionalReviewRequirement
11. Manual/connected mode improvements

This order strengthens the current branch without jumping prematurely into real external integrations.
