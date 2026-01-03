from fastapi.testclient import TestClient
import app
client = TestClient(app.app)
# Test unauthenticated invest
resp = client.post('/api/invest', json={
    'bondId': 0,
    'investorAddress': '0xabc',
    'amount': 100,
    'timestamp': '2026-01-03T00:00:00',
    'transactionHash': '0xdeadbeef'
})
print('Unauthenticated invest status:', resp.status_code, resp.text)
# Register a user
reg = client.post('/api/auth/register', json={'email':'test@example.com','username':'tester','password':'secret123'})
print('Register status', reg.status_code, reg.text)
if reg.status_code==200:
    token = reg.json().get('access_token')
    # Try invest with token
    resp2 = client.post('/api/invest', json={
        'bondId': 0,
        'investorAddress': '0xabc',
        'amount': 100,
        'timestamp': '2026-01-03T00:00:00',
        'transactionHash': '0xdeadbeef'
    }, headers={'Authorization': 'Bearer ' + token})
    print('Authenticated invest status:', resp2.status_code, resp2.text)
else:
    print('Registration failed, cannot test authenticated invest')
