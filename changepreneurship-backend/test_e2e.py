"""Quick E2E test script — run inside backend container"""
import requests

BASE = "http://localhost:5000/api"

# Login
r = requests.post(f"{BASE}/auth/login",
    json={"email": "alex@invoiceflow.io", "password": "Alex2026!"},
    headers={"Content-Type": "application/json"})
d = r.json()
token = d.get("session_token")
print(f"LOGIN: {r.status_code} token={token[:15] if token else 'NONE'}...")

if not token:
    print("Cannot continue without token")
    exit(1)

H = {"Authorization": f"Bearer {token}"}

# Progress phases
r2 = requests.get(f"{BASE}/v1/progress/phases", headers=H)
d2 = r2.json()
print(f"\nPHASES: {r2.status_code}")
for p in d2.get("phases", []):
    print(f"  {p['id']}: {p['status']} {p['progress_percentage']}%")

# Ventures active
r3 = requests.get(f"{BASE}/v1/ventures/active", headers=H)
d3 = r3.json()
v = (d3.get("data") or {}).get("venture") or d3.get("venture") or {}
print(f"\nVENTURE: {r3.status_code} idea={str(v.get('idea_clarified',''))[:50]}")

# Profile / phase gates
r4 = requests.get(f"{BASE}/v1/ventures/profile", headers=H)
d4 = r4.json()
print(f"\nPROFILE: {r4.status_code}")
gates = (d4.get("data") or d4).get("phase_gates", {})
matrix = (d4.get("data") or d4).get("founder_matrix") or {}
print(f"  phase_gates: {gates}")
print(f"  recommended_route: {matrix.get('recommended_route')}")

# Next action
r5 = requests.get(f"{BASE}/v1/progress/next-action", headers=H)
d5 = r5.json()
na = (d5.get("data") or d5).get("next_action") or {}
print(f"\nNEXT ACTION: {r5.status_code} type={na.get('type')} phase={na.get('phase_id')}")
