# UI Cleanup - Manual Testing Checklist

**Dev Server:** http://localhost:5174/  
**Status:** Running ✅

## 🧪 Test Scenarios

### 1. Landing Page Navigation
- [ ] Go to `http://localhost:5174/`
- [ ] Click "Continue Assessment" button → Should go to `/assessment`
- [ ] Click "AI Insights" button → Should go to `/ai-insights`
- [ ] Click "View Dashboard" button → Should go to `/dashboard` (was `/user-dashboard`)

### 2. Main Dashboard Routes
- [ ] Navigate to `http://localhost:5174/dashboard`
  - [ ] Page loads without errors
  - [ ] Shows UserDashboard component (progress tracking)
  - [ ] Check console for no errors
  
- [ ] Navigate to `http://localhost:5174/ai-insights`
  - [ ] Page loads without errors
  - [ ] Shows ExecutiveSummaryDashboard (AI analysis)
  - [ ] Check console for no errors

### 3. Backward Compatibility (Redirects)
Test old URLs redirect correctly:

- [ ] `http://localhost:5174/user-dashboard` → Redirects to `/dashboard`
- [ ] `http://localhost:5174/dashboard/executive-summary` → Redirects to `/ai-insights`
- [ ] `http://localhost:5174/ai-recommendations` → Redirects to `/ai-insights`
- [ ] `http://localhost:5174/ai-insights/recommendations` → Redirects to `/ai-insights`

### 4. Removed Routes (Should 404 or redirect to home)
- [ ] `http://localhost:5174/adaptive-demo` → Should redirect to `/` (404 fallback)
- [ ] `http://localhost:5174/simple-adaptive` → Should redirect to `/` (404 fallback)

### 5. NavBar Links
- [ ] Click "Back" button (if not on home)
- [ ] Click "Home" button → Goes to `/`
- [ ] Click "AI Insights" button (when authenticated) → Goes to `/ai-insights`
- [ ] NavBar highlights active route correctly

### 6. Assessment Flow
- [ ] Go to `/assessment`
- [ ] Select a phase (e.g., Self Discovery)
- [ ] Complete some questions
- [ ] Navigate between phases
- [ ] No broken navigation

### 7. User Settings
- [ ] Go to `/profile`
  - [ ] Profile settings page loads
  - [ ] No console errors
  
- [ ] Go to `/assessment-history`
  - [ ] History page loads
  - [ ] No console errors

### 8. Browser Console Check
- [ ] Open DevTools (F12)
- [ ] Navigate through all routes
- [ ] Check for:
  - [ ] No 404 errors for missing components
  - [ ] No import errors
  - [ ] No React warnings about deprecated components
  - [ ] No infinite redirect loops

### 9. Mobile Responsiveness
- [ ] Toggle device toolbar (Ctrl+Shift+M)
- [ ] Test navigation on mobile viewport
- [ ] Check all buttons are accessible
- [ ] No layout breaks

---

## ✅ Expected Results

**All routes should:**
- Load without errors
- Show correct component
- Have working navigation
- No console warnings about missing imports

**Redirects should:**
- Happen instantly
- Update URL in address bar
- Work on first visit (no refresh needed)

---

## 🐛 If Issues Found

### Common Issues & Fixes

**Issue:** "Cannot find module" error
- **Fix:** Check if import path is correct in App.jsx
- **Fix:** Verify component wasn't accidentally deleted

**Issue:** Redirect loop
- **Fix:** Check Navigate component doesn't point back to same route
- **Fix:** Ensure no circular redirects

**Issue:** 404 on valid route
- **Fix:** Check Route path spelling in App.jsx
- **Fix:** Ensure component is properly imported

**Issue:** Component renders but with errors
- **Fix:** Check if component has dependencies on deleted components
- **Fix:** Update any hardcoded links to old routes

---

## 📝 Test Results

**Date Tested:** _________________  
**Tester:** _________________  
**Browser:** _________________  

### Summary
- Total tests: 40+
- Passed: _____
- Failed: _____
- Notes: _________________

---

## 🚀 After Testing

If all tests pass:
1. ✅ Mark UI cleanup as complete
2. ✅ Update main documentation
3. ✅ Consider deleting `_deprecated` folder after 2 weeks
4. ✅ Deploy to staging
5. ✅ Monitor analytics for 404s

If tests fail:
1. ❌ Document failures in this file
2. ❌ Fix issues in App.jsx or component files
3. ❌ Re-run tests
4. ❌ Consider rollback if major issues
