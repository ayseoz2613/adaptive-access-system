# Taha Emre Orhan – Demo Scenarios (Week 6)

This document provides repeatable demo flows for Authentication → Risk Engine → Trust Score behavior.

## Preconditions
- Backend running on: http://localhost:5001
- Frontend running on: http://localhost:5173
- A test user exists (e.g., taha@test.com)
- Browser DevTools available

## Scenario A – Normal Login (SAFE → Dashboard)
1. Open Login page.
2. Login with correct credentials from the same browser/device.
Expected:
- ui_state = allow
- access_token returned
- Navigate to /dashboard
- Risk level SAFE, low score
- Trust score visible in UI

## Scenario B – Suspicious Login (SUSPICIOUS → MFA_REQUIRED)
Goal: Trigger MFA_REQUIRED with suspicious signals.
Method options:
- Rapid wrong-password attempts then correct password
- Simulate device change (different browser/incognito)
Expected:
- ui_state = mfa (or error=MFA_REQUIRED)
- No dashboard access until MFA success
- User is prompted to verify identity

## Scenario C – Critical Login (CRITICAL → Decoy)
Goal: Trigger Decoy routing.
Method options:
- Combine multiple risk factors (device change + ip change)
- Use a low trust score profile (if supported)
Expected:
- ui_state = decoy
- Redirect to /decoy
- Real dashboard must NOT be accessible

## Scenario D – Backend Down (UI Fallback Behavior)
1. Stop backend.
2. Attempt login.
Expected:
- UI shows “Backend unreachable”
- Test mode is allowed only if explicitly enabled in code (dev only)

## Notes
- Screenshots of each scenario should be captured and attached to final presentation evidence.
