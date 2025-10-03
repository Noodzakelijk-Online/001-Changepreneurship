"""
Principles Service - Data access layer for entrepreneurship principles
"""
import json
import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class PrinciplesService:
    def __init__(self, principles_file: str | None = None):
        if principles_file is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            principles_file = os.path.join(base_dir, "data", "principles.json")
        self.principles_file = principles_file
        self._principles = None
        self._load_principles()

    def _load_principles(self):
        """Load principles from JSON file"""
        try:
            if os.path.exists(self.principles_file):
                with open(self.principles_file, 'r', encoding='utf-8') as f:
                    self._principles = json.load(f)
            else:
                self._principles = []
        except Exception as e:
            logger.error(f"Error loading principles: {e}")
            self._principles = []

    def get_all_principles(self) -> List[Dict]:
        """Get all principles"""
        return self._principles or []

    def get_principles_by_category(self, category: str, limit: int = 5) -> List[Dict]:
        """Get principles filtered by category"""
        if not self._principles:
            return []

        filtered: List[Dict] = []
        for principle in self._principles:
            categories = principle.get('categories', [])
            if category.lower() in [cat.lower() for cat in categories]:
                filtered.append(principle)
                if len(filtered) >= limit:
                    break

        return filtered

    def get_principles_by_stage(self, stage: str, limit: int = 5) -> List[Dict]:
        """Get principles filtered by business stage"""
        if not self._principles:
            return []

        filtered: List[Dict] = []
        for principle in self._principles:
            stages = principle.get('business_stage', [])
            if stage.lower() in [s.lower() for s in stages]:
                filtered.append(principle)
                if len(filtered) >= limit:
                    break

        return filtered

    def get_principles_by_category_and_stage(
        self,
        category: str | None = None,
        stage: str | None = None,
        limit: int = 5,
    ) -> List[Dict]:
        """Get principles filtered by both category and stage"""
        if not self._principles:
            return []

        filtered: List[Dict] = []
        for principle in self._principles:
            category_match = True
            stage_match = True

            if category:
                categories = principle.get('categories', [])
                category_match = category.lower() in [cat.lower() for cat in categories]

            if stage:
                stages = principle.get('business_stage', [])
                stage_match = stage.lower() in [s.lower() for s in stages]

            if category_match and stage_match:
                filtered.append(principle)
                if len(filtered) >= limit:
                    break

        return filtered

    def get_principle_by_id(self, principle_id: int) -> Optional[Dict]:
        """Get a specific principle by ID"""
        if not self._principles:
            return None

        for principle in self._principles:
            if principle.get('id') == principle_id:
                return principle

        return None

    def search_principles(self, query: str, limit: int = 5) -> List[Dict]:
        """Search principles by title or summary"""
        if not self._principles or not query:
            return []

        query_lower = query.lower()
        filtered: List[Dict] = []

        for principle in self._principles:
            title = principle.get('title', '').lower()
            summary = principle.get('short_summary', '').lower()

            if query_lower in title or query_lower in summary:
                filtered.append(principle)
                if len(filtered) >= limit:
                    break

        return filtered

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        if not self._principles:
            return []

        categories = set()
        for principle in self._principles:
            for category in principle.get('categories', []):
                categories.add(category)

        return sorted(list(categories))

    def get_stages(self) -> List[str]:
        """Get all unique business stages"""
        if not self._principles:
            return []

        stages = set()
        for principle in self._principles:
            for stage in principle.get('business_stage', []):
                stages.add(stage)

        return sorted(list(stages))

    def get_recommendations(
        self,
        user_stage: str | None,
        focus_areas: List[str] | None = None,
        limit: int = 5,
    ) -> List[Dict]:
        """Generate personalized principle recommendations."""
        if not self._principles:
            return []

        recommendations: List[Dict] = []

        # Recommendations based on user's business stage
        if user_stage:
            stage_principles = self.get_principles_by_stage(user_stage, limit)
            recommendations.extend(stage_principles)

        # Recommendations based on focus areas/categories
        if focus_areas:
            for area in focus_areas:
                area_principles = self.get_principles_by_category(area, 2)
                recommendations.extend(area_principles)

        # Remove duplicates while preserving order
        seen_ids = set()
        unique_recommendations: List[Dict] = []
        for principle in recommendations:
            pid = principle.get('id')
            if pid not in seen_ids:
                unique_recommendations.append(principle)
                seen_ids.add(pid)

        return unique_recommendations[:limit]
