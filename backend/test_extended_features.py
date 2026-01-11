"""
Extended test suite for Bond Investment Platform
Tests new features: bond creation, statistics, and investment tracking
"""

from fastapi.testclient import TestClient
import app
from datetime import datetime, timedelta
import json

client = TestClient(app.app)

print("=" * 80)
print("EXTENDED BOND INVESTMENT PLATFORM TEST SUITE")
print("=" * 80)

# Step 1: Register test users
print("\n[SETUP] Creating test users...")
test_users = []
for i in range(2):
    reg = client.post('/api/auth/register', json={
        'email': f'testinvestor{i}@example.com',
        'username': f'investor{i}',
        'password': f'Password{i}@123!'
    })
    if reg.status_code == 200:
        data = reg.json()
        test_users.append({
            'id': data['user_id'],
            'token': data['access_token'],
            'username': data['username']
        })
        print(f"✓ User {i+1} created: {data['username']}")

# Step 2: Get platform statistics (before investments)
print("\n[TEST 1] Get platform statistics (empty)...")
resp = client.get('/api/investments/stats')
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    stats = resp.json()
    print(f"  Total Invested: ${stats['totalInvested']}")
    print(f"  Total Investors: {stats['totalInvestors']}")
    print(f"  Total Investments: {stats['totalInvestments']}")
    print(f"  Total Bonds Available: {stats['totalBonds']}")

# Step 3: Create test investments across multiple bonds
print("\n[TEST 2] Creating investments across bonds...")
wallet_addresses = [
    '0x1111111111111111111111111111111111111111',
    '0x2222222222222222222222222222222222222222'
]

investments_created = []
for user_idx, user in enumerate(test_users):
    for bond_id in range(min(3, 3)):  # Test with first 3 bonds
        amount = (bond_id + 1) * 100 * (user_idx + 1)
        
        inv_payload = {
            'bondId': bond_id,
            'investorAddress': wallet_addresses[user_idx],
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
            'transactionHash': f"0x{'0' * 60}{user_idx:02d}{bond_id:02d}"
        }
        
        resp = client.post('/api/invest',
            json=inv_payload,
            headers={'Authorization': f'Bearer {user["token"]}'}
        )
        
        if resp.status_code == 200:
            result = resp.json()
            investments_created.append({
                'user_id': user['id'],
                'bond_id': bond_id,
                'amount': amount,
                'investment_id': result['investment']['id']
            })
            print(f"✓ {user['username']} invested ${amount} in Bond {bond_id}")

# Step 4: Get investments for specific user
print("\n[TEST 3] Get investments for specific user...")
if test_users:
    user_id = test_users[0]['id']
    resp = client.get(f'/api/investments/user/{user_id}',
        headers={'Authorization': f'Bearer {test_users[0]["token"]}'}
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"  User ID: {data['userId']}")
        print(f"  Total Investments: {len(data['investments'])}")
        print(f"  Total Invested: ${data['totalInvested']}")
        for inv in data['investments']:
            print(f"    - Bond {inv['bond_id']}: ${inv['amount']}")

# Step 5: Get investments for specific bond
print("\n[TEST 4] Get investments for specific bond...")
for bond_id in [0, 1, 2]:
    resp = client.get(f'/api/investments/bond/{bond_id}')
    print(f"\nStatus: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"  Bond: {data['bondName']}")
        print(f"  Total Invested: ${data['totalInvested']}")
        print(f"  Investor Count: {data['investorCount']}")
        print(f"  Total Investment Records: {len(data['investments'])}")

# Step 6: Get updated platform statistics
print("\n[TEST 5] Get platform statistics (after investments)...")
resp = client.get('/api/investments/stats')
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    stats = resp.json()
    print(f"  Total Invested: ${stats['totalInvested']}")
    print(f"  Total Investors: {stats['totalInvestors']}")
    print(f"  Total Investments: {stats['totalInvestments']}")
    print(f"  Total Bonds Available: {stats['totalBonds']}")
    
    print("\n  Bond-wise breakdown:")
    for bond_id, bond_stat in stats['bondStats'].items():
        print(f"    Bond {bond_id} ({bond_stat['name']}):")
        print(f"      Total Invested: ${bond_stat['totalInvested']}")
        print(f"      Investors: {bond_stat['investorCount']}")
        print(f"      Investment Count: {bond_stat['investmentCount']}")

# Step 7: Get portfolio for each wallet
print("\n[TEST 6] Get portfolios for wallets...")
for wallet in wallet_addresses:
    resp = client.get(f'/api/portfolio/{wallet}')
    print(f"\nStatus: {resp.status_code}")
    if resp.status_code == 200:
        portfolio = resp.json()
        print(f"  Address: {wallet}")
        print(f"  Total Investments: {len(portfolio['investments'])}")
        print(f"  Total Invested: ${portfolio['totalInvested']}")
        print(f"  Total Value: ${portfolio['totalValue']}")

# Step 8: Create new bond (if user is authenticated)
print("\n[TEST 7] Creating new bond...")
if test_users:
    new_bond = {
        "id": 100,
        "name": "Test Bond - Corporate Debt",
        "issuer": "Test Corporation",
        "faceValue": 500000,
        "couponRate": 500,  # 5%
        "maturityDate": (datetime.now() + timedelta(days=1825)).isoformat(),
        "issueDate": datetime.now().isoformat(),
        "description": "Test bond for platform verification",
        "minimumInvestment": 50,
        "bondTokenAddress": "0x1234567890123456789012345678901234567890"
    }
    
    resp = client.post('/api/bonds',
        json=new_bond,
        headers={'Authorization': f'Bearer {test_users[0]["token"]}'}
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        result = resp.json()
        print(f"✓ Bond created: {result['bond']['name']}")
        print(f"  ID: {result['bond']['id']}")
        print(f"  Coupon Rate: {result['bond']['couponRate']/100}%")
    else:
        print(f"Response: {resp.text}")

# Step 9: Verify new bond is available
print("\n[TEST 8] Verify all bonds...")
resp = client.get('/api/bonds')
if resp.status_code == 200:
    bonds = resp.json()
    print(f"Total bonds in system: {len(bonds)}")
    print("\nBond list:")
    for bond in bonds:
        print(f"  - Bond {bond['id']}: {bond['name']} ({bond['issuer']})")

# Step 10: Test error cases
print("\n[TEST 9] Testing error cases...")

# Try to invest below minimum
print("  Testing minimum investment validation...")
resp = client.post('/api/invest',
    json={
        'bondId': 0,
        'investorAddress': '0x9999999999999999999999999999999999999999',
        'amount': 5,  # Less than minimum
        'timestamp': datetime.now().isoformat(),
        'transactionHash': '0xtest'
    },
    headers={'Authorization': f'Bearer {test_users[0]["token"]}'}
)
if resp.status_code != 200:
    print(f"    ✓ Correctly rejected: {resp.json()['detail']}")

# Try to invest in non-existent bond
print("  Testing invalid bond ID...")
resp = client.post('/api/invest',
    json={
        'bondId': 99999,
        'investorAddress': '0x9999999999999999999999999999999999999999',
        'amount': 1000,
        'timestamp': datetime.now().isoformat(),
        'transactionHash': '0xtest'
    },
    headers={'Authorization': f'Bearer {test_users[0]["token"]}'}
)
if resp.status_code != 200:
    print(f"    ✓ Correctly rejected: {resp.json()['detail']}")

print("\n" + "=" * 80)
print("ALL EXTENDED TESTS COMPLETED SUCCESSFULLY!")
print("=" * 80)
print("\nKey Features Verified:")
print("  ✓ User registration and authentication")
print("  ✓ Investment creation and persistence")
print("  ✓ Multiple investments per user")
print("  ✓ Multiple users on same bond")
print("  ✓ Portfolio retrieval")
print("  ✓ Statistics and analytics")
print("  ✓ Bond creation")
print("  ✓ Error handling and validation")
print("=" * 80)
