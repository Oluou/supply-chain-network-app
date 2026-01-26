
"""
Test script for usaspending-orm integration (latest API).
Queries subawards to extract recipient (supplier) and prime contractor using USASpendingClient.
"""

from usaspending import USASpendingClient

def test_subawards_supplier_prime():
    print("Querying subawards for supplier and prime contractor info...")
    with USASpendingClient() as client:
        # Search for awards, limit to 20 for demo
        awards = client.awards.search().contracts().limit(20).all()
        for award in awards:
            if getattr(award, 'subaward_count', 0) > 0:
                for subaward in award.subawards:
                    supplier = subaward.recipient.name if subaward.recipient else "N/A"
                    prime = award.recipient.name if award.recipient else "N/A"
                    print(f"Subaward ID: {getattr(subaward, 'subaward_number', 'N/A')}, Amount: {getattr(subaward, 'amount', 'N/A')}, Supplier: {supplier}, Prime Contractor: {prime}")

if __name__ == "__main__":
    test_subawards_supplier_prime()
