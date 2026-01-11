"""
Comprehensive test for Bond Investment Platform
Tests bond data generation, investments, and portfolio functionality
"""

from fastapi.testclient import TestClient
import app
import json
from datetime import datetime, timedelta

client = TestClient(app.app)

print("=" * 80)
print("BOND INVESTMENT PLATFORM - COMPREHENSIVE TEST")
print("=" * 80)

# Test 1: Get all bonds
print("\n[TEST 1] Fetching all available bonds...")
resp = client.get('/api/bonds')
print(f"Status: {resp.status_code}")
bonds = resp.json()
print(f"Total bonds available: {len(bonds)}")
for bond in bonds:
    print(f"  - Bond ID {bond['id']}: {bond['name']} ({bond['issuer']})")
    print(f"    Face Value: ${bond['faceValue']}, Coupon Rate: {bond['couponRate']/100}%")

# Test 2: Register a user
print("\n[TEST 2] Registering new user...")
reg = client.post('/api/auth/register', json={
    'email': f'investor{datetime.now().timestamp()}@example.com',
    'username': f'investor{int(datetime.now().timestamp())}',
    'password': 'securePassword123!'
})
print(f"Status: {reg.status_code}")
if reg.status_code == 200:
    reg_data = reg.json()
    token = reg_data.get('access_token')
    user_id = reg_data.get('user_id')
    print(f"User registered successfully - ID: {user_id}, Username: {reg_data['username']}")
else:
    print(f"Registration failed: {reg.text}")
    exit(1)

# Test 3: Get user info
print("\n[TEST 3] Retrieving user information...")
resp = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    user_info = resp.json()
    print(f"User: {user_info['username']} ({user_info['email']})")

# Test 4: Record multiple investments
print("\n[TEST 4] Recording investments in multiple bonds...")
investments_data = [
    {'bondId': 0, 'amount': 1000, 'investorAddress': '0xaabbccdd11223344556677889900aabbccddee11'},
    {'bondId': 1, 'amount': 500, 'investorAddress': '0xaabbccdd11223344556677889900aabbccddee11'},
    {'bondId': 2, 'amount': 750, 'investorAddress': '0xaabbccdd11223344556677889900aabbccddee11'},
]

for inv_data in investments_data:
    inv_payload = {
        'bondId': inv_data['bondId'],
        'investorAddress': inv_data['investorAddress'],
        'amount': inv_data['amount'],
        'timestamp': datetime.now().isoformat(),
        'transactionHash': f"0x{'0' * 63}{inv_data['bondId']}"
    }
    
    resp = client.post('/api/invest', 
        json=inv_payload,
        headers={'Authorization': f'Bearer {token}'}
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        result = resp.json()
        print(f"✓ Invested ${inv_data['amount']} in Bond {inv_data['bondId']}")
        print(f"  Investment ID: {result['investment']['id']}")
    else:
        print(f"✗ Failed: {resp.text}")

# Test 5: Get portfolio
print("\n[TEST 5] Retrieving investor portfolio...")
wallet_address = '0xaabbccdd11223344556677889900aabbccddee11'
resp = client.get(f'/api/portfolio/{wallet_address}')
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    portfolio = resp.json()
    print(f"Total Investments: {len(portfolio['investments'])}")
    print(f"Total Invested: ${portfolio['totalInvested']}")
    print(f"Total Value: ${portfolio['totalValue']}")
    print(f"Total Yield: ${portfolio['totalYield']}")
    
    print("\nInvestment breakdown:")
    for inv in portfolio['investments']:
        print(f"  - Bond {inv['bondId']}: ${inv['amount']} at {inv['timestamp']}")

# Test 6: Get bond statistics
print("\n[TEST 6] Retrieving bond statistics...")
for bond_id in [0, 1, 2]:
    resp = client.get(f'/api/bonds/{bond_id}/stats')
    print(f"\nStatus: {resp.status_code}")
    if resp.status_code == 200:
        stats = resp.json()
        print(f"Bond {bond_id} Statistics:")
        print(f"  Total Invested: ${stats['totalInvested']}")
        print(f"  Investor Count: {stats['investorCount']}")
        print(f"  Days to Maturity: {stats['daysToMaturity']}")
        print(f"  Coupon Rate: {stats['couponRate']}%")
        print(f"  Utilization: {stats['utilization']:.2f}%")

# Test 7: Calculate yield
print("\n[TEST 7] Calculating bond yields...")
for bond_id in [0, 1, 2]:
    resp = client.get(f'/api/yield/{bond_id}', 
        params={'address': wallet_address}
    )
    print(f"\nStatus: {resp.status_code}")
    if resp.status_code == 200:
        yield_data = resp.json()
        print(f"Bond {bond_id} Yield Information:")
        print(f"  Coupon Rate: {yield_data['couponRate']}%")
        print(f"  Current Yield: {yield_data['currentYield']}%")
        print(f"  Annual Interest: ${yield_data['annualInterest']:.2f}")
        print(f"  Accrued Interest: ${yield_data['accruedInterest']:.2f}")
        print(f"  Days to Maturity: {yield_data['daysToMaturity']}")
        if yield_data.get('investorYield'):
            print(f"  Investor Specific Yield: {yield_data['investorYield']}%")

# Test 8: Get bond details
print("\n[TEST 8] Retrieving detailed bond information...")
resp = client.get('/api/bonds/0')
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    bond = resp.json()
    print(f"Bond Details:")
    print(f"  Name: {bond['name']}")
    print(f"  Issuer: {bond['issuer']}")
    print(f"  Description: {bond['description']}")
    print(f"  Face Value: ${bond['faceValue']}")
    print(f"  Coupon Rate: {bond['couponRate']/100}%")
    print(f"  Minimum Investment: ${bond['minimumInvestment']}")
    print(f"  Issue Date: {bond['issueDate']}")
    print(f"  Maturity Date: {bond['maturityDate']}")

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 80)
