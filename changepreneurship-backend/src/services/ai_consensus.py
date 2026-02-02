"""
AI Consensus Service - Multi-LLM Analysis for Business Insights
Uses free tier APIs: Google Gemini, Groq (Llama 3), HuggingFace (Mistral)
"""
import os
import requests
import json
from typing import Dict, List, Optional

class AIConsensusService:
    """Service for generating consensus business insights from multiple LLMs"""
    
    def __init__(self):
        self.gemini_key = os.getenv('GOOGLE_API_KEY')
        self.groq_key = os.getenv('GROQ_API_KEY')
        self.huggingface_key = os.getenv('HUGGINGFACE_API_KEY')
        
    def generate_consensus(self, user_responses: Dict, phase_data: Dict) -> Dict:
        """
        Generate consensus insights from multiple LLMs
        
        Args:
            user_responses: User's assessment responses across all phases
            phase_data: Metadata about completed assessment phases
            
        Returns:
            Dict with consensus insights, recommendations, and individual LLM responses
        """
        # Prepare business summary from user data
        business_summary = self._prepare_business_summary(user_responses, phase_data)
        
        # Query multiple LLMs
        llm_responses = []
        
        if self.gemini_key:
            gemini_response = self._query_gemini(business_summary)
            if gemini_response:
                llm_responses.append({
                    'model': 'Google Gemini',
                    'response': gemini_response
                })
        
        if self.groq_key:
            groq_response = self._query_groq(business_summary)
            if groq_response:
                llm_responses.append({
                    'model': 'Groq Llama 3',
                    'response': groq_response
                })
        
        if self.huggingface_key:
            hf_response = self._query_huggingface(business_summary)
            if hf_response:
                llm_responses.append({
                    'model': 'HuggingFace Mistral',
                    'response': hf_response
                })
        
        # Extract consensus
        if llm_responses:
            consensus = self._extract_consensus(llm_responses)
        else:
            # Fallback if no API keys configured
            consensus = self._fallback_analysis(business_summary)
        
        return {
            'success': True,
            'consensus': consensus,
            'llm_responses': llm_responses,
            'business_summary': business_summary
        }
    
    def _prepare_business_summary(self, responses: Dict, phases: Dict) -> str:
        """Prepare structured business summary from user responses"""
        summary_parts = []
        
        # Extract key information from responses
        for phase_id, phase_responses in responses.items():
            phase_name = phase_id.replace('_', ' ').title()
            summary_parts.append(f"\n## {phase_name}")
            
            for response in phase_responses[:5]:  # Top 5 responses per phase
                question_id = response.get('question_id', 'unknown')
                value = response.get('response_value', '')
                if value and len(str(value)) > 10:
                    summary_parts.append(f"- {question_id}: {value[:200]}")
        
        return "\n".join(summary_parts)
    
    def _query_gemini(self, business_summary: str) -> Optional[str]:
        """Query Google Gemini API"""
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Analyze this business plan and provide 3 key insights:\n\n{business_summary}"
                    }]
                }]
            }
            
            response = requests.post(
                f"{url}?key={self.gemini_key}",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"Gemini API error: {e}")
        
        return None
    
    def _query_groq(self, business_summary: str) -> Optional[str]:
        """Query Groq API (Llama 3)"""
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "user",
                        "content": f"Analyze this business plan and provide 3 key insights:\n\n{business_summary}"
                    }
                ],
                "max_tokens": 500
            }
            
            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
        except Exception as e:
            print(f"Groq API error: {e}")
        
        return None
    
    def _query_huggingface(self, business_summary: str) -> Optional[str]:
        """Query HuggingFace Inference API (Mistral)"""
        try:
            url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
            
            payload = {
                "inputs": f"Analyze this business plan and provide 3 key insights:\n\n{business_summary}",
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.7
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.huggingface_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return data[0]['generated_text'] if isinstance(data, list) else data.get('generated_text', '')
        except Exception as e:
            print(f"HuggingFace API error: {e}")
        
        return None
    
    def _extract_consensus(self, llm_responses: List[Dict]) -> Dict:
        """Extract consensus from multiple LLM responses"""
        # Simple consensus: combine insights from all models
        all_insights = []
        
        for resp in llm_responses:
            text = resp['response']
            # Extract key points (simple split by newlines)
            lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 20]
            all_insights.extend(lines[:3])  # Top 3 from each
        
        return {
            'key_insights': all_insights[:5],  # Top 5 overall
            'models_consulted': len(llm_responses),
            'confidence': 'high' if len(llm_responses) >= 2 else 'medium'
        }
    
    def _fallback_analysis(self, business_summary: str) -> Dict:
        """Fallback analysis when no API keys are available"""
        return {
            'key_insights': [
                "Your business plan shows comprehensive market research and clear value proposition.",
                "Consider validating your target market assumptions with real customer interviews.",
                "Financial projections should include sensitivity analysis for key variables.",
                "Team composition and skill gaps need to be addressed for successful execution.",
                "Risk mitigation strategies are well-defined but need ongoing monitoring."
            ],
            'models_consulted': 0,
            'confidence': 'fallback',
            'note': 'Configure API keys (GOOGLE_API_KEY, GROQ_API_KEY, HUGGINGFACE_API_KEY) for AI-powered insights'
        }
