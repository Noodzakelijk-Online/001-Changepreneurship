/**
 * ValueZonePage — redirect to Venture Profile (Sprint 21)
 * Value Zone is now a panel on the Venture Profile page.
 */
import { Navigate } from 'react-router-dom';

export default function ValueZonePage() {
  return <Navigate to="/venture-profile" replace />;
}
