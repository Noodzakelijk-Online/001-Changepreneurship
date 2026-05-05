/**
 * MindMappingPage — redirect to Idea Discovery (Sprint 21)
 * Mind Map concept is now Phase 2 — Idea Discovery.
 */
import { Navigate } from 'react-router-dom';

export default function MindMappingPage() {
  return <Navigate to="/assessment/idea-discovery" replace />;
}
