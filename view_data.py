"""
View scraped awarded contracts data.

This script displays the scraped data in a readable format.

Usage:
    python view_data.py              # Show first 5 records
    python view_data.py --all        # Show all records
    python view_data.py --limit 10   # Show first 10 records
"""

import sys
import argparse
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent / 'bidintel-main' / 'backend'))

from models.database import Database


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='View scraped awarded contracts data')
    parser.add_argument('--limit', type=int, default=5, help='Number of records to show (default: 5)')
    parser.add_argument('--all', action='store_true', help='Show all records')
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    print("\n" + "="*80)
    print("📊 AWARDED CONTRACTS DATA")
    print("="*80)

    db = Database()

    # Get total count
    all_awards = db.get_all_awarded_contracts(limit=1000)
    total = len(all_awards)

    print(f"\n📈 Total records in database: {total}")

    if total == 0:
        print("\n⚠️  No data found. Run the scraper first:")
        print("   python scrape_2_pages.py")
        return

    # Get records to display
    limit = None if args.all else args.limit
    awards = db.get_all_awarded_contracts(limit=limit)

    print(f"📋 Showing: {len(awards)} record(s)")
    print("="*80)

    # Display each award
    for i, award in enumerate(awards, 1):
        print(f"\n{'='*80}")
        print(f"🏆 AWARD #{i} - {award.award_notice_number}")
        print(f"{'='*80}")

        # Identifiers
        print(f"\n📋 IDENTIFIERS:")
        print(f"   Award Notice Number: {award.award_notice_number}")
        print(f"   Bid Reference Number: {award.bid_reference_number or 'N/A'}")
        print(f"   Control Number: {award.control_number or 'N/A'}")

        # Awardee
        print(f"\n🏆 AWARDEE (WINNER):")
        print(f"   Company: {award.awardee_name or 'N/A'}")
        print(f"   Contact Person: {award.awardee_contact_person or 'N/A'}")
        if award.awardee_address:
            addr = award.awardee_address[:100] + "..." if len(award.awardee_address) > 100 else award.awardee_address
            print(f"   Address: {addr}")

        # Financial
        print(f"\n💰 FINANCIAL:")
        if award.approved_budget:
            print(f"   ABC (Approved Budget): PHP {award.approved_budget:,.2f}")
        else:
            print(f"   ABC (Approved Budget): N/A")

        if award.contract_amount:
            print(f"   Contract Amount (Won For): PHP {award.contract_amount:,.2f}")
        else:
            print(f"   Contract Amount (Won For): N/A")

        if award.approved_budget and award.contract_amount:
            savings = award.approved_budget - award.contract_amount
            pct = (savings / award.approved_budget) * 100
            print(f"   💡 Savings: PHP {savings:,.2f} ({pct:.1f}%)")

        # Contract details
        print(f"\n📝 CONTRACT DETAILS:")
        if award.award_title:
            title = award.award_title[:80] + "..." if len(award.award_title) > 80 else award.award_title
            print(f"   Title: {title}")
        print(f"   Classification: {award.classification or 'N/A'}")
        print(f"   Period: {award.period_of_contract or 'N/A'}")
        print(f"   Award Date: {award.award_date or 'N/A'}")
        print(f"   Contract Number: {award.contract_number or 'N/A'}")

        # Procuring entity
        print(f"\n🏛️ PROCURING ENTITY:")
        print(f"   Agency: {award.procuring_entity or 'N/A'}")
        if award.agency_address:
            addr = award.agency_address[:80] + "..." if len(award.agency_address) > 80 else award.agency_address
            print(f"   Address: {addr}")
        print(f"   Delivery Location: {award.delivery_location or 'N/A'}")

        # Other info
        print(f"\n📅 OTHER INFO:")
        print(f"   Procurement Mode: {award.procurement_mode or 'N/A'}")
        print(f"   Category: {award.category or 'N/A'}")
        print(f"   Funding Source: {award.funding_source or 'N/A'}")
        print(f"   Created By: {award.created_by or 'N/A'}")
        print(f"   Publish Date: {award.publish_date or 'N/A'}")

        # Documents
        if award.documents:
            print(f"\n📄 DOCUMENTS ({len(award.documents)}):")
            for doc in award.documents:
                print(f"   • {doc.document_type or 'Document'}: {doc.filename}")
                print(f"     URL: {doc.document_url}")
        else:
            print(f"\n📄 DOCUMENTS: None found")

    print("\n" + "="*80)
    print("✅ END OF DATA")
    print("="*80)

    # Stats summary
    if total > 0:
        print(f"\n📊 QUICK STATS:")

        total_abc = sum(a.approved_budget for a in all_awards if a.approved_budget)
        total_contract = sum(a.contract_amount for a in all_awards if a.contract_amount)
        total_savings = total_abc - total_contract

        print(f"   Total ABC: PHP {total_abc:,.2f}")
        print(f"   Total Contract Amount: PHP {total_contract:,.2f}")
        print(f"   Total Savings: PHP {total_savings:,.2f}")
        if total_abc > 0:
            avg_savings_pct = (total_savings / total_abc) * 100
            print(f"   Average Savings: {avg_savings_pct:.1f}%")

        # Count unique entities
        unique_agencies = len(set(a.procuring_entity for a in all_awards if a.procuring_entity))
        unique_awardees = len(set(a.awardee_name for a in all_awards if a.awardee_name))

        print(f"\n   Unique Procuring Entities: {unique_agencies}")
        print(f"   Unique Awardees: {unique_awardees}")

    print("\n💡 Tips:")
    print("   - Use --all to see all records")
    print("   - Use --limit N to see N records")
    print("   - Data is in: philgeps_data.db")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
