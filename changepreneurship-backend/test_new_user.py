import requests
BASE = "http://localhost:5000/api"
r = requests.post(BASE+"/auth/login", json={"email":"test@local.dev","password":"Test1234!"}, headers={"Content-Type":"application/json"})
d = r.json()
print("login:", r.status_code, list(d.keys()))
token = d.get("session_token","")
if token:
    r2 = requests.get(BASE+"/v1/progress/phases", headers={"Authorization":"Bearer "+token})
    print("phases:", r2.status_code, r2.text[:300])
    r3 = requests.get(BASE+"/v1/progress/next-action", headers={"Authorization":"Bearer "+token})
    print("next-action:", r3.status_code, r3.text[:300])
    r4 = requests.get(BASE+"/v1/ventures/profile", headers={"Authorization":"Bearer "+token})
    print("profile:", r4.status_code, r4.text[:300])
