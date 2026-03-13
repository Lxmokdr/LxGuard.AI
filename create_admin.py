import requests

try:
    url = "http://localhost:8002/admin/auth/register-first-admin?email=admin@admin.com&password=admin"
    r = requests.post(url)
    print("Status:", r.status_code)
    print("Response:", r.text)
except Exception as e:
    print(e)
