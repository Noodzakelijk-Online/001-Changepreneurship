import io
import re
from datetime import datetime

from pypdf import PdfReader


SKILL_CLUSTERS = {
    'product': ['product', 'roadmap', 'user research', 'ux', 'feature', 'backlog', 'discovery'],
    'engineering': ['python', 'javascript', 'react', 'node', 'api', 'backend', 'frontend', 'engineering', 'software'],
    'sales': ['sales', 'account executive', 'closing', 'pipeline', 'crm', 'bdr'],
    'marketing': ['marketing', 'seo', 'content', 'brand', 'growth', 'acquisition', 'campaign'],
    'operations': ['operations', 'process', 'supply chain', 'logistics', 'project management'],
    'finance': ['finance', 'financial', 'fp&a', 'budget', 'forecast', 'pricing'],
    'leadership': ['manager', 'head of', 'director', 'lead', 'led', 'managed', 'built team'],
}

INDUSTRY_KEYWORDS = {
    'saas': ['saas', 'software as a service'],
    'fintech': ['fintech', 'payments', 'banking', 'finance'],
    'healthtech': ['healthtech', 'healthcare', 'medical', 'clinical'],
    'edtech': ['edtech', 'education', 'learning'],
    'ecommerce': ['ecommerce', 'e-commerce', 'retail', 'shopify'],
    'b2b': ['b2b', 'enterprise'],
    'consumer': ['consumer', 'b2c'],
    'ai': ['ai', 'artificial intelligence', 'machine learning', 'llm'],
}


class ResumeAnalysisService:
    def extract_text(self, file_storage):
        filename = (file_storage.filename or '').lower()
        data = file_storage.read()
        file_storage.stream.seek(0)

        if filename.endswith('.pdf'):
            reader = PdfReader(io.BytesIO(data))
            return '\n'.join((page.extract_text() or '') for page in reader.pages).strip()

        try:
            return data.decode('utf-8', errors='ignore').strip()
        except Exception:
            return ''

    def analyze(self, text):
        normalized = re.sub(r'\s+', ' ', text or '').strip()
        lower = normalized.lower()
        lines = [line.strip() for line in (text or '').splitlines() if line.strip()]

        email = self._search(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', normalized)
        phone = self._search(r'(\+?\d[\d\s().-]{7,}\d)', normalized)
        linkedin_url = self._search(r'https?://(?:www\.)?linkedin\.com/[^\s]+', normalized)

        years_experience = self._infer_years_experience(lower)
        current_role = self._infer_current_role(lines)
        skill_clusters = self._infer_clusters(lower, SKILL_CLUSTERS)
        industries = self._infer_clusters(lower, INDUSTRY_KEYWORDS)
        leadership_strength = 'leadership' in skill_clusters
        education_level = self._infer_education(lower)
        completeness_score = self._compute_completeness_score(
            email=email,
            phone=phone,
            current_role=current_role,
            years_experience=years_experience,
            skill_clusters=skill_clusters,
            industries=industries,
            text_length=len(normalized),
        )

        founder_strengths = []
        if 'product' in skill_clusters:
            founder_strengths.append('Strong product discovery and customer understanding signal')
        if 'engineering' in skill_clusters:
            founder_strengths.append('Technical execution signal that supports faster MVP iteration')
        if 'sales' in skill_clusters or 'marketing' in skill_clusters:
            founder_strengths.append('Go-to-market signal from commercial or growth experience')
        if leadership_strength:
            founder_strengths.append('Leadership signal suggests better team-building and execution leverage')
        if years_experience >= 8:
            founder_strengths.append('Meaningful professional depth that can translate into founder credibility')
        if not founder_strengths:
            founder_strengths.append('Some professional experience detected, but not enough signal for strong specialization yet')

        likely_edges = []
        if 'fintech' in industries or 'healthtech' in industries or 'edtech' in industries:
            likely_edges.append('Domain expertise signal can improve founder-market fit in regulated or specialized markets')
        if 'b2b' in industries or 'saas' in industries:
            likely_edges.append('Good signal for B2B workflow, SaaS, or service-led startup opportunities')
        if 'consumer' in industries or 'marketing' in skill_clusters:
            likely_edges.append('Potential strength in consumer positioning, messaging, or acquisition')

        possible_gaps = []
        if 'engineering' not in skill_clusters:
            possible_gaps.append('Technical build capability is not strongly visible from the CV')
        if 'sales' not in skill_clusters and 'marketing' not in skill_clusters:
            possible_gaps.append('Go-to-market and distribution strength is not strongly visible from the CV')
        if not leadership_strength:
            possible_gaps.append('Leadership or team management evidence is limited')
        if completeness_score < 55:
            possible_gaps.append('The uploaded CV is sparse, so the system should treat this as weak enrichment rather than a high-confidence founder profile')

        strongest_matches = self._venture_fit(skill_clusters, industries, positive=True)
        weaker_matches = self._venture_fit(skill_clusters, industries, positive=False)

        recommendations = []
        if 'engineering' not in skill_clusters:
            recommendations.append('If pursuing a software-heavy venture, consider validating technical execution support early')
        if 'sales' not in skill_clusters and 'marketing' not in skill_clusters:
            recommendations.append('Strengthen customer discovery and go-to-market planning before scaling the idea')
        if not industries:
            recommendations.append('Add more domain context through assessment answers because the CV alone does not show a clear market edge')
        if not recommendations:
            recommendations.append('Use this profile as an additive founder-fit signal, then combine it with assessment answers for stronger venture recommendations')

        parsed_data = {
            'contact': {
                'email': email,
                'phone': phone,
                'linkedin_url': linkedin_url,
            },
            'inferred_profile': {
                'current_role': current_role,
                'years_experience': years_experience,
                'education_level': education_level,
                'skill_clusters': skill_clusters,
                'industries': industries,
                'leadership_signal': leadership_strength,
                'completeness_score': completeness_score,
            },
            'generated_at': datetime.utcnow().isoformat(),
        }

        analysis = {
            'summary': self._build_summary(current_role, years_experience, skill_clusters, industries, completeness_score),
            'founder_strengths': founder_strengths,
            'likely_edges': likely_edges,
            'possible_gaps': possible_gaps,
            'venture_fit': {
                'strongest_matches': strongest_matches,
                'weaker_matches': weaker_matches,
            },
            'recommendations': recommendations,
            'confidence': min(95, max(35, completeness_score)),
        }

        suggested_profile = {
            'currentRole': current_role or '',
            'experience': years_experience or '',
        }

        return {
            'parsed_data': parsed_data,
            'analysis': analysis,
            'suggested_profile': suggested_profile,
        }

    def _search(self, pattern, text):
        match = re.search(pattern, text or '', flags=re.IGNORECASE)
        return match.group(0).strip() if match else ''

    def _infer_current_role(self, lines):
        for line in lines[:12]:
            if len(line) > 80:
                continue
            lower = line.lower()
            if any(token in lower for token in ['engineer', 'manager', 'director', 'founder', 'product', 'designer', 'consultant', 'analyst', 'marketer', 'sales']):
                return line
        return lines[1] if len(lines) > 1 else ''

    def _infer_years_experience(self, text):
        explicit = re.search(r'(\d{1,2})\+?\s+years?', text)
        if explicit:
            return int(explicit.group(1))

        years = [int(y) for y in re.findall(r'\b(20\d{2}|19\d{2})\b', text)]
        if years:
            earliest = min(years)
            return max(0, min(datetime.utcnow().year - earliest, 40))
        return 0

    def _infer_clusters(self, text, mapping):
        found = []
        for label, keywords in mapping.items():
            if any(keyword in text for keyword in keywords):
                found.append(label)
        return found

    def _infer_education(self, text):
        if any(token in text for token in ['phd', 'doctorate']):
            return 'doctorate'
        if any(token in text for token in ['master', 'msc', 'mba']):
            return 'masters'
        if any(token in text for token in ['bachelor', 'bsc', 'ba ']):
            return 'bachelors'
        return 'unknown'

    def _compute_completeness_score(self, **kwargs):
        score = 20
        if kwargs.get('email'):
            score += 10
        if kwargs.get('phone'):
            score += 5
        if kwargs.get('current_role'):
            score += 15
        if kwargs.get('years_experience'):
            score += 15
        score += min(len(kwargs.get('skill_clusters', [])) * 8, 20)
        score += min(len(kwargs.get('industries', [])) * 5, 10)
        if kwargs.get('text_length', 0) > 1200:
            score += 5
        return min(score, 100)

    def _venture_fit(self, skill_clusters, industries, positive=True):
        positives = []
        negatives = []

        if 'engineering' in skill_clusters and 'saas' in industries:
            positives.append('B2B SaaS or workflow tools')
        if 'product' in skill_clusters:
            positives.append('Discovery-heavy digital products')
        if 'sales' in skill_clusters or 'marketing' in skill_clusters:
            positives.append('Service-led or distribution-sensitive ventures')
        if 'operations' in skill_clusters:
            positives.append('Operationally complex or execution-heavy businesses')
        if 'fintech' in industries or 'healthtech' in industries or 'edtech' in industries:
            positives.append('Domain-specific ventures where background knowledge matters')

        if 'engineering' not in skill_clusters:
            negatives.append('Deep-tech products that require strong in-house technical execution from day one')
        if 'sales' not in skill_clusters and 'marketing' not in skill_clusters:
            negatives.append('Acquisition-heavy products that depend on strong early distribution mechanics')
        if not industries:
            negatives.append('Highly domain-specific ventures where prior market context is a major advantage')

        values = positives if positive else negatives
        if not values:
            values = ['Generalist-friendly early-stage opportunities'] if positive else ['No strong negative fit detected from CV alone']
        return values[:3]

    def _build_summary(self, current_role, years_experience, skill_clusters, industries, completeness_score):
        role_text = current_role or 'Background signal is limited'
        skills_text = ', '.join(skill_clusters[:3]) if skill_clusters else 'no strong specialization detected'
        industries_text = ', '.join(industries[:2]) if industries else 'no clear domain specialization detected'
        years_text = f'{years_experience}+ years of experience' if years_experience else 'experience duration unclear'
        return (
            f'{role_text}. Resume suggests {years_text}, with visible strength clusters in {skills_text}. '
            f'Domain exposure appears strongest in {industries_text}. Confidence in this enrichment is {completeness_score}%.'
        )