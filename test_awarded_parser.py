"""
Test script for awarded contracts parser.

Tests the parser with the reference HTML files to ensure it can extract
all the required fields correctly.
"""

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent / 'bidintel-main' / 'backend'))

from scraper.parser import PhilGEPSParser
import json


def test_awarded_contract_detail():
    """Test parsing awarded contract detail page."""
    print("=" * 70)
    print("Testing Awarded Contract Detail Parser")
    print("=" * 70)

    # Read reference HTML
    html_path = Path(__file__).parent / 'reference' / 'PhilGEPS Awarded Contracts Detail.html'

    if not html_path.exists():
        print(f"❌ Reference HTML not found: {html_path}")
        return False

    print(f"📄 Reading: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Parse
    print("\n🔍 Parsing HTML...")
    parser = PhilGEPSParser(html)

    try:
        award_data = parser.parse_awarded_contract()

        print("\n✅ Parsing successful!")
        print("\n" + "=" * 70)
        print("EXTRACTED DATA")
        print("=" * 70)

        # Display key fields
        print(f"\n📋 IDENTIFIERS:")
        print(f"   Award Notice Number: {award_data.get('award_notice_number')}")
        print(f"   Bid Reference Number: {award_data.get('bid_reference_number')}")
        print(f"   Control Number: {award_data.get('control_number')}")

        print(f"\n🏆 AWARDEE INFORMATION:")
        print(f"   Awardee Name: {award_data.get('awardee_name')}")
        print(f"   Contact Person: {award_data.get('awardee_contact_person')}")
        print(f"   Address: {award_data.get('awardee_address')}")
        print(f"   Corporate Title: {award_data.get('awardee_corporate_title')}")

        print(f"\n💰 FINANCIAL INFORMATION:")
        print(f"   ABC (Approved Budget): PHP {award_data.get('approved_budget'):,.2f}" if award_data.get('approved_budget') else "   ABC: None")
        print(f"   Contract Amount (Awarded Price): PHP {award_data.get('contract_amount'):,.2f}" if award_data.get('contract_amount') else "   Contract Amount: None")

        if award_data.get('approved_budget') and award_data.get('contract_amount'):
            savings = award_data['approved_budget'] - award_data['contract_amount']
            savings_pct = (savings / award_data['approved_budget']) * 100
            print(f"   💡 Savings: PHP {savings:,.2f} ({savings_pct:.2f}%)")

        print(f"\n📅 DATES:")
        print(f"   Award Date: {award_data.get('award_date')}")
        print(f"   Publish Date: {award_data.get('publish_date')}")
        print(f"   Date Created: {award_data.get('date_created')}")
        print(f"   Date Last Updated: {award_data.get('date_last_updated')}")

        print(f"\n📝 CONTRACT DETAILS:")
        print(f"   Contract Number: {award_data.get('contract_number') or 'N/A'}")
        print(f"   Period of Contract: {award_data.get('period_of_contract')}")
        print(f"   Contract Effectivity Date: {award_data.get('contract_effectivity_date') or 'N/A'}")
        print(f"   Contract End Date: {award_data.get('contract_end_date') or 'N/A'}")
        print(f"   Proceed Date: {award_data.get('proceed_date') or 'N/A'}")

        print(f"\n🏢 PROCUREMENT INFORMATION:")
        print(f"   Award Title: {award_data.get('award_title')}")
        print(f"   Award Type: {award_data.get('award_type')}")
        print(f"   Classification: {award_data.get('classification')}")
        print(f"   Procurement Mode: {award_data.get('procurement_mode')}")
        print(f"   Category: {award_data.get('category')}")
        print(f"   Procurement Rules: {award_data.get('procurement_rules')}")

        print(f"\n🏛️ PROCURING ENTITY:")
        print(f"   Entity: {award_data.get('procuring_entity')}")
        print(f"   Delivery Location: {award_data.get('delivery_location')}")
        print(f"   Funding Source: {award_data.get('funding_source')}")
        print(f"   Created By: {award_data.get('created_by')}")

        # Check for missing critical fields
        print("\n" + "=" * 70)
        print("VALIDATION CHECKS")
        print("=" * 70)

        critical_fields = {
            'award_notice_number': 'Award Notice Number',
            'awardee_name': 'Awardee Name',
            'approved_budget': 'ABC (Approved Budget)',
            'contract_amount': 'Contract Amount (Awarded Price)',
            'award_date': 'Award Date'
        }

        missing_fields = []
        for field, label in critical_fields.items():
            if not award_data.get(field):
                missing_fields.append(label)
                print(f"❌ Missing: {label}")
            else:
                print(f"✅ Found: {label}")

        if missing_fields:
            print(f"\n⚠️  Warning: {len(missing_fields)} critical field(s) missing")
            return False
        else:
            print(f"\n✅ All critical fields extracted successfully!")
            return True

    except Exception as e:
        print(f"\n❌ Error parsing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n🧪 AWARDED CONTRACTS PARSER TEST SUITE\n")

    success = test_awarded_contract_detail()

    print("\n" + "=" * 70)
    if success:
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print("\n💡 Next steps:")
        print("   1. The parser is working correctly")
        print("   2. You can now run the scraper: python bidintel-main/backend/run_awarded_scraper.py")
        print("   3. Or test with a few pages first: python bidintel-main/backend/run_awarded_scraper.py --workers 1")
        return 0
    else:
        print("❌ TESTS FAILED")
        print("=" * 70)
        print("\n💡 Check the errors above and fix the parser")
        return 1


if __name__ == "__main__":
    sys.exit(main())
