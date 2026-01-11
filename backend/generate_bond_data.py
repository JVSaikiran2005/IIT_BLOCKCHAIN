"""
Generate additional bond data for the Bond Investment Platform
This script creates sample bonds with various characteristics
"""

from fastapi.testclient import TestClient
import app
from datetime import datetime, timedelta
import json

client = TestClient(app.app)

# Sample bonds with different characteristics
ADDITIONAL_BONDS = [
    {
        "id": 3,
        "name": "Japanese Government Bond (JGB) 10-Year",
        "issuer": "Ministry of Finance Japan",
        "faceValue": 2000000,  # ¥2M equivalent
        "couponRate": 100,  # 1.0% annual
        "maturityDate": (datetime.now() + timedelta(days=3650)).isoformat(),
        "issueDate": datetime.now().isoformat(),
        "description": "10-year Japanese government bond with semi-annual interest payments",
        "minimumInvestment": 50,  # ¥50 minimum
        "bondTokenAddress": "0x0000000000000000000000000000000000000003"
    },
    {
        "id": 4,
        "name": "Australian Government Bond (AGB) 7-Year",
        "issuer": "Australian Office of Financial Management",
        "faceValue": 1500000,  # A$1.5M equivalent
        "couponRate": 380,  # 3.8% annual
        "maturityDate": (datetime.now() + timedelta(days=2555)).isoformat(),
        "issueDate": datetime.now().isoformat(),
        "description": "7-year Australian government bond with annual interest payments",
        "minimumInvestment": 25,  # A$25 minimum
        "bondTokenAddress": "0x0000000000000000000000000000000000000004"
    },
    {
        "id": 5,
        "name": "Canadian Government Bond (CGB) 5-Year",
        "issuer": "Department of Finance Canada",
        "faceValue": 1200000,  # C$1.2M equivalent
        "couponRate": 420,  # 4.2% annual
        "maturityDate": (datetime.now() + timedelta(days=1825)).isoformat(),
        "issueDate": datetime.now().isoformat(),
        "description": "5-year Canadian government bond with semi-annual interest payments",
        "minimumInvestment": 18,  # C$18 minimum
        "bondTokenAddress": "0x0000000000000000000000000000000000000005"
    },
    {
        "id": 6,
        "name": "Singapore Government Securities (SGS) 3-Year",
        "issuer": "Monetary Authority of Singapore",
        "faceValue": 500000,  # S$500K equivalent
        "couponRate": 290,  # 2.9% annual
        "maturityDate": (datetime.now() + timedelta(days=1095)).isoformat(),
        "issueDate": datetime.now().isoformat(),
        "description": "3-year Singapore government security with annual interest payments",
        "minimumInvestment": 12,  # S$12 minimum
        "bondTokenAddress": "0x0000000000000000000000000000000000000006"
    },
    {
        "id": 7,
        "name": "Swiss Federal Bonds (Conf) 15-Year",
        "issuer": "Swiss Federal Finance Administration",
        "faceValue": 3000000,  # CHF 3M equivalent
        "couponRate": 180,  # 1.8% annual
        "maturityDate": (datetime.now() + timedelta(days=5475)).isoformat(),
        "issueDate": datetime.now().isoformat(),
        "description": "15-year Swiss federal bond with annual interest payments. Highly rated AAA",
        "minimumInvestment": 30,  # CHF 30 minimum
        "bondTokenAddress": "0x0000000000000000000000000000000000000007"
    },
    {
        "id": 8,
        "name": "Corporate Green Bond - Tech Finance Corp",
        "issuer": "Tech Finance Corp (AAA Rated)",
        "faceValue": 500000,  # $500K
        "couponRate": 550,  # 5.5% annual - higher yield for corporate
        "maturityDate": (datetime.now() + timedelta(days=1825)).isoformat(),
        "issueDate": datetime.now().isoformat(),
        "description": "5-year corporate green bond financing renewable energy projects. ESG compliant.",
        "minimumInvestment": 100,  # $100 minimum
        "bondTokenAddress": "0x0000000000000000000000000000000000000008"
    },
    {
        "id": 9,
        "name": "Emerging Market Bond - Brazil Development Bank",
        "issuer": "Brazilian Development Bank (BNDES)",
        "faceValue": 800000,  # BRL equivalent
        "couponRate": 650,  # 6.5% annual - higher yield for emerging market
        "maturityDate": (datetime.now() + timedelta(days=1460)).isoformat(),
        "issueDate": datetime.now().isoformat(),
        "description": "4-year emerging market bond from leading Brazilian development institution. Higher risk, higher yield.",
        "minimumInvestment": 200,  # BRL equivalent
        "bondTokenAddress": "0x0000000000000000000000000000000000000009"
    },
    {
        "id": 10,
        "name": "Inflation-Linked Bond (TIPS) - US Treasury",
        "issuer": "United States Treasury",
        "faceValue": 1000000,  # $1M
        "couponRate": 200,  # 2.0% base + inflation adjustment
        "maturityDate": (datetime.now() + timedelta(days=2190)).isoformat(),
        "issueDate": datetime.now().isoformat(),
        "description": "6-year US Treasury Inflation-Protected Security. Principal adjusts with CPI. Protection against inflation.",
        "minimumInvestment": 25,  # $25 minimum
        "bondTokenAddress": "0x000000000000000000000000000000000000000A"
    }
]

print("=" * 80)
print("BOND DATA GENERATION SCRIPT")
print("=" * 80)

# First, get current bonds
print("\n[STEP 1] Fetching existing bonds...")
resp = client.get('/api/bonds')
existing_bonds = resp.json()
print(f"Existing bonds: {len(existing_bonds)}")

# Note: In the current implementation, bonds are stored in memory in BondService
# To persist new bonds, we would need to save them to database
# For now, we'll just show the bonds that will be added

print("\n[STEP 2] Additional bonds to be generated:")
for bond in ADDITIONAL_BONDS:
    print(f"\n  Bond ID {bond['id']}: {bond['name']}")
    print(f"    Issuer: {bond['issuer']}")
    print(f"    Face Value: ${bond['faceValue']}")
    print(f"    Coupon Rate: {bond['couponRate']/100}%")
    print(f"    Maturity: {bond['maturityDate'][:10]}")
    print(f"    Min Investment: ${bond['minimumInvestment']}")

print("\n[STEP 3] Creating JSON file for bond data...")
bonds_output = {
    "timestamp": datetime.now().isoformat(),
    "totalBonds": len(existing_bonds) + len(ADDITIONAL_BONDS),
    "existingBonds": existing_bonds,
    "additionalBonds": ADDITIONAL_BONDS
}

with open('bond_data_catalog.json', 'w') as f:
    json.dump(bonds_output, f, indent=2)

print("✓ Generated bond_data_catalog.json with all bond information")

print("\n[STEP 4] Summary:")
print(f"  Total bonds in system: {len(existing_bonds)}")
print(f"  New bonds generated: {len(ADDITIONAL_BONDS)}")
print(f"  Total after generation: {len(existing_bonds) + len(ADDITIONAL_BONDS)}")

print("\n" + "=" * 80)
print("BOND DATA GENERATION COMPLETED!")
print("=" * 80)
print("\nTo add these bonds to the live system, run the backend with:")
print("  uvicorn backend.app:app --reload")
print("\nThen use the POST /api/bonds endpoint to create new bonds.")
