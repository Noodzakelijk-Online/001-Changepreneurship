"""
MicroMentor Integration — Sprint 4 (S4-02)
============================================
CEO (Section 12.1): External Integration — Mentorship Outreach System.

"The system PROPOSES a message. The user APPROVES it. The system SENDS it.
 A copy of the content sent is logged and hashed."

Supported operations:
  SEARCH_MENTORS     — AUTO_APPROVE (no external send)
  DRAFT_OUTREACH     — AUTO_APPROVE (draft, not sent)
  SEND_OUTREACH      — REQUIRES_APPROVAL (sends externally)
  DRAFT_FOLLOWUP     — AUTO_APPROVE
  SEND_FOLLOWUP      — REQUIRES_APPROVAL

This is an MVP stub — actual OAuth + MicroMentor API calls to be implemented
when OAuth credentials are available. The interface is complete.
"""
import logging
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)

# Platform identifier for audit logging
PLATFORM_MICROMENTOR = 'micromentor'


@dataclass
class MentorProfile:
    id: str
    name: str
    expertise: List[str]
    location: str
    bio: str
    availability: str
    match_score: float  # 0.0-1.0


@dataclass
class OutreachDraft:
    subject: str
    body: str
    mentor_id: str
    platform: str
    estimated_read_time_seconds: int


class MicroMentorIntegration:
    """
    MVP stub — interface complete, API calls are mocked.
    Replace _search_api / _send_api with real HTTP calls when ready.
    """

    def search_mentors(
        self,
        expertise_tags: List[str],
        location: Optional[str] = None,
        max_results: int = 5,
    ) -> List[MentorProfile]:
        """
        Search for mentors matching expertise tags.
        AUTO_APPROVE — read-only, no external send.
        Returns structured mentor list for UI display.
        """
        # MVP: return mock data
        results = self._search_api(expertise_tags, location, max_results)
        logger.info(
            "MicroMentor search: %s tags, location=%s → %d results",
            expertise_tags, location, len(results),
        )
        return results

    def draft_outreach(
        self,
        mentor: MentorProfile,
        founder_context: dict,
    ) -> OutreachDraft:
        """
        Draft an outreach message using founder context.
        AUTO_APPROVE — this is a draft only, not sent.
        founder_context: {venture_summary, specific_ask, founder_name}
        """
        draft = self._compose_outreach(mentor, founder_context)
        logger.info("MicroMentor outreach drafted for mentor=%s", mentor.id)
        return draft

    def send_outreach(
        self,
        draft: OutreachDraft,
        oauth_token: str,
    ) -> dict:
        """
        REQUIRES_APPROVAL — sends the approved outreach message.
        Returns send receipt with message_id.
        Called only after UserActionService.mark_executed().
        """
        if not oauth_token:
            raise ValueError('OAuth token required to send outreach')
        result = self._send_api(draft, oauth_token)
        logger.info(
            "MicroMentor outreach sent to mentor=%s result=%s",
            draft.mentor_id, result.get('status'),
        )
        return result

    def get_connection_status(self, oauth_token: Optional[str]) -> dict:
        """Check if MicroMentor OAuth is connected."""
        return {
            'platform': PLATFORM_MICROMENTOR,
            'connected': bool(oauth_token),
            'scopes': ['read:mentors', 'send:messages'] if oauth_token else [],
        }

    # ------------------------------------------------------------------
    # Stub API calls — replace with real HTTP + OAuth in v2
    # ------------------------------------------------------------------

    def _search_api(
        self,
        expertise_tags: List[str],
        location: Optional[str],
        max_results: int,
    ) -> List[MentorProfile]:
        """MVP stub — returns mock mentors."""
        tags_str = ', '.join(expertise_tags)
        return [
            MentorProfile(
                id=f'mentor_{i}',
                name=f'Mentor {i}',
                expertise=expertise_tags[:2],
                location=location or 'Remote',
                bio=f'Experienced in {tags_str}.',
                availability='Available',
                match_score=round(0.9 - i * 0.1, 2),
            )
            for i in range(min(3, max_results))
        ]

    def _compose_outreach(
        self,
        mentor: MentorProfile,
        founder_context: dict,
    ) -> OutreachDraft:
        """MVP stub — template-based outreach draft."""
        name = founder_context.get('founder_name', 'Founder')
        ask = founder_context.get('specific_ask', 'discuss my venture idea')
        venture = founder_context.get('venture_summary', 'an early-stage venture')
        expertise = ', '.join(mentor.expertise[:2]) if mentor.expertise else 'your area of expertise'

        subject = f"Seeking guidance on {expertise} — {name}"
        body = (
            f"Hi {mentor.name},\n\n"
            f"My name is {name}, and I'm building {venture}. "
            f"I'm reaching out because your background in {expertise} aligns with a challenge I'm navigating.\n\n"
            f"Specifically, I'd love to {ask}.\n\n"
            f"Would you be open to a 20-minute conversation? I'm flexible on timing.\n\n"
            f"Best,\n{name}"
        )
        return OutreachDraft(
            subject=subject,
            body=body,
            mentor_id=mentor.id,
            platform=PLATFORM_MICROMENTOR,
            estimated_read_time_seconds=45,
        )

    def _send_api(self, draft: OutreachDraft, oauth_token: str) -> dict:
        """MVP stub — simulates a successful send."""
        return {
            'status': 'sent',
            'message_id': f'msg_{draft.mentor_id}_{id(draft)}',
            'platform': PLATFORM_MICROMENTOR,
        }
