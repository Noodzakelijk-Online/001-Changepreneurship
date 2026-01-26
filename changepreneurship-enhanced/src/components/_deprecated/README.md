# Deprecated Components

**Date:** 2026-01-27  
**Reason:** UI Cleanup - Consolidation and removal of unused demo pages

## Components Moved Here

### Demo Components (Deleted from Routes)
- `AdaptiveDemo.jsx` - Adaptive assessment demo (unused)
- `SimpleAdaptiveDemo.jsx` - Simple adaptive demo (unused)

### Duplicate AI Components (Consolidated)
- `AIInsightsHub.jsx` - Hub page that just linked to other pages
  - **Replaced by:** Direct navigation to `/ai-insights` (ExecutiveSummaryDashboard)
  
- `AIRecommendationsSimple.jsx` - Simple AI recommendations
- `AIRecommendationsReal.jsx` + `AIRecommendationsReal.css` - Real AI recommendations
  - **Replaced by:** Consolidated into ExecutiveSummaryDashboard tabs
  - **Old routes:** `/ai-recommendations`, `/ai-insights/recommendations`
  - **New route:** `/ai-insights` (with tabs for different views)

## Migration Guide

### Old URLs → New URLs
| Old URL | New URL | Notes |
|---------|---------|-------|
| `/user-dashboard` | `/dashboard` | UserDashboard - cleaner URL |
| `/dashboard/executive-summary` | `/ai-insights` | ExecutiveSummaryDashboard |
| `/ai-recommendations` | `/ai-insights` | Merged into main AI dashboard |
| `/ai-insights/recommendations` | `/ai-insights` | Merged into main AI dashboard |
| `/adaptive-demo` | *removed* | Demo page |
| `/simple-adaptive` | *removed* | Demo page |

All old URLs have redirect routes for backward compatibility.

## Current Active Dashboards

1. **`/dashboard`** - UserDashboard (progress tracking, phase completion)
2. **`/ai-insights`** - ExecutiveSummaryDashboard (AI analysis, business insights)

## Safe to Delete?

These files can be safely deleted after:
- ✅ Verifying all redirects work
- ✅ Testing main user flows
- ✅ Confirming no external links point to old URLs
- ✅ Keeping for 1-2 weeks as backup

**Recommendation:** Keep for 2 weeks, then delete permanently.
