"""
Test script: Search for NASA contracts to SpaceX in 2023 and print any attached subawards.
Follows usaspending-orm documentation and prints relevant award and subaward info.
"""

from usaspending import USASpendingClient

def main():
    print("Searching for NASA contracts to SpaceX in 2023...")
    with USASpendingClient() as client:
        awards_query = client.awards.search() \
            .agency("National Aeronautics and Space Administration") \
            .recipient_search_text("Space Exploration Technologies") \
            .contracts() \
            .fiscal_year(2023) \
            .order_by("Award Amount", "desc")

        awards = awards_query.limit(10).all()
        if not awards:
            print("No awards found.")
            return
        for award in awards:
            print(f"\nAward: {award.award_identifier}")
            print(f"  Description: {award.description}")
            print(f"  Total Obligation: {award.total_obligation}")
            print(f"  Recipient: {award.recipient.name if award.recipient else 'N/A'}")
            print(f"  Subaward Count: {getattr(award, 'subaward_count', 0)}")
            if getattr(award, 'subaward_count', 0) > 0:
                for subaward in award.subawards:
                    supplier = subaward.recipient.name if subaward.recipient else "N/A"
                    print(f"    Subaward ID: {getattr(subaward, 'subaward_number', 'N/A')}, Amount: {getattr(subaward, 'amount', 'N/A')}, Supplier: {supplier}")

if __name__ == "__main__":
    main()