"""
Final Verification Test - Bond Investment Platform
Verifies all investment features are working correctly
"""

from fastapi.testclient import TestClient
import app
from datetime import datetime

client = TestClient(app.app)

print("\n" + "=" * 80)
print("FINAL VERIFICATION TEST - BOND INVESTMENT PLATFORM")
print("=" * 80)

checks_passed = 0
checks_failed = 0

def verify(name, condition):
    global checks_passed, checks_failed
    if condition:
        print(f"✓ {name}")
        checks_passed += 1
    else:
        print(f"✗ {name}")
        checks_failed += 1

# Test 1: Bonds Loading
print("\n[CHECK 1] Bond Data Loading")
resp = client.get('/api/bonds')
verify("Bonds endpoint returns 200", resp.status_code == 200)
bonds = resp.json()
verify("At least 3 bonds available", len(bonds) >= 3)
verify("Each bond has required fields", all(
    'id' in b and 'name' in b and 'issuer' in b and 'couponRate' in b 
    for b in bonds
))

# Test 2: User Registration
print("\n[CHECK 2] User Registration")
reg_resp = client.post('/api/auth/register', json={
    'email': f'verify{datetime.now().timestamp()}@test.com',
    'username': f'verify_user_{int(datetime.now().timestamp())}',
    'password': 'TestPassword123'
})
verify("Registration successful", reg_resp.status_code == 200)
if reg_resp.status_code == 200:
    token = reg_resp.json().get('access_token')
    user_id = reg_resp.json().get('user_id')
    verify("Token provided", token is not None)
    verify("User ID provided", user_id is not None)
else:
    token = None
    user_id = None

# Test 3: Authentication
print("\n[CHECK 3] Authentication")
if token:
    auth_resp = client.get('/api/auth/me', 
        headers={'Authorization': f'Bearer {token}'}
    )
    verify("Can retrieve user info with token", auth_resp.status_code == 200)

# Test 4: Investment Creation
print("\n[CHECK 4] Investment Creation")
if token and user_id:
    inv_resp = client.post('/api/invest', 
        json={
            'bondId': 0,
            'investorAddress': '0xtest123',
            'amount': 500,
            'timestamp': datetime.now().isoformat(),
            'transactionHash': '0xhash'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    verify("Investment creation successful", inv_resp.status_code == 200)
    if inv_resp.status_code == 200:
        inv_data = inv_resp.json()
        verify("Investment has ID", 'id' in inv_data.get('investment', {}))
        verify("Response indicates success", inv_data.get('success') == True)

# Test 5: Investment Validation
print("\n[CHECK 5] Investment Validation")
if token:
    # Try investment below minimum
    bad_inv = client.post('/api/invest',
        json={
            'bondId': 0,
            'investorAddress': '0xtest456',
            'amount': 1,  # Below minimum
            'timestamp': datetime.now().isoformat(),
            'transactionHash': '0xhash2'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    verify("Rejects investment below minimum", bad_inv.status_code != 200)
    
    # Try non-existent bond
    bad_bond = client.post('/api/invest',
        json={
            'bondId': 99999,
            'investorAddress': '0xtest789',
            'amount': 100,
            'timestamp': datetime.now().isoformat(),
            'transactionHash': '0xhash3'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    verify("Rejects non-existent bond", bad_bond.status_code != 200)

# Test 6: Portfolio Management
print("\n[CHECK 6] Portfolio Management")
portfolio_resp = client.get('/api/portfolio/0xtest123')
verify("Portfolio endpoint available", portfolio_resp.status_code == 200)
if portfolio_resp.status_code == 200:
    portfolio = portfolio_resp.json()
    verify("Portfolio has required fields", all(
        k in portfolio for k in ['address', 'investments', 'totalInvested']
    ))

# Test 7: Statistics
print("\n[CHECK 7] Statistics")
stats_resp = client.get('/api/investments/stats')
verify("Statistics endpoint available", stats_resp.status_code == 200)
if stats_resp.status_code == 200:
    stats = stats_resp.json()
    verify("Statistics has required fields", all(
        k in stats for k in ['totalInvested', 'totalInvestors', 'totalInvestments', 'totalBonds']
    ))
    verify("Total bonds count correct", stats['totalBonds'] >= 3)

# Test 8: Bond Statistics
print("\n[CHECK 8] Bond Statistics")
bond_stats_resp = client.get('/api/bonds/0/stats')
verify("Bond stats endpoint available", bond_stats_resp.status_code == 200)
if bond_stats_resp.status_code == 200:
    bond_stats = bond_stats_resp.json()
    verify("Bond stats has required fields", all(
        k in bond_stats for k in ['bondId', 'totalInvested', 'investorCount']
    ))

# Test 9: Bond Investments Endpoint
print("\n[CHECK 9] Bond Investments Endpoint")
bond_inv_resp = client.get('/api/investments/bond/0')
verify("Bond investments endpoint available", bond_inv_resp.status_code == 200)
if bond_inv_resp.status_code == 200:
    bond_inv = bond_inv_resp.json()
    verify("Bond investments has required fields", all(
        k in bond_inv for k in ['bondId', 'investments', 'totalInvested']
    ))

# Test 10: Yield Calculations
print("\n[CHECK 10] Yield Calculations")
yield_resp = client.get('/api/yield/0')
verify("Yield endpoint available", yield_resp.status_code == 200)
if yield_resp.status_code == 200:
    yield_data = yield_resp.json()
    verify("Yield data has required fields", all(
        k in yield_data for k in ['couponRate', 'currentYield', 'daysToMaturity']
    ))
    verify("Yield calculations are positive", yield_data['currentYield'] > 0)

# Test 11: Database Persistence
print("\n[CHECK 11] Database Persistence")
try:
    import sqlite3
    conn = sqlite3.connect('bond_platform.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM investments")
    investment_count = cursor.fetchone()[0]
    conn.close()
    verify("Database has investments", investment_count >= 1)
    verify("Multiple investments recorded", investment_count >= 3)
except Exception as e:
    verify("Database accessible", False)

# Print Summary
print("\n" + "=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)
print(f"✓ Passed: {checks_passed}")
print(f"✗ Failed: {checks_failed}")
print(f"Total: {checks_passed + checks_failed}")

success_rate = (checks_passed / (checks_passed + checks_failed) * 100) if (checks_passed + checks_failed) > 0 else 0
print(f"\nSuccess Rate: {success_rate:.1f}%")

if checks_failed == 0:
    print("\n✓✓✓ ALL CHECKS PASSED - INVESTMENT FEATURES WORKING CORRECTLY ✓✓✓")
else:
    print(f"\n⚠ {checks_failed} checks failed - please review errors above")

print("=" * 80 + "\n")
