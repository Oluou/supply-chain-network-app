"""
Prototype: USAspending Data Ingestion for Network Graph
Extracts funding agencies, program offices, primes, and suppliers from USAspending ORM
and outputs normalized nodes and edges for network construction.
"""
from usaspending import USASpendingClient
import json
import decimal

# Node and edge containers
g_nodes = {}
g_edges = []

def add_node(node_id, node_type, **attrs):
    g_nodes[node_id] = {"id": node_id, "type": node_type, **attrs}

def add_edge(source, target, edge_type, **attrs):
    g_edges.append({"source": source, "target": target, "type": edge_type, **attrs})

def extract_awards(fy=2023, agency="Department of Defense", limit=10):
    with USASpendingClient() as client:
        awards = client.awards.search() \
            .agency(agency) \
            .contracts() \
            .fiscal_year(fy) \
            .order_by("Award Amount", "desc") \
            .limit(limit).all()
        for award in awards:
            # Funding agency node
            try:
                print("DEBUG awarding_agency:", award.awarding_agency.__dict__)
            except Exception as e:
                print("DEBUG awarding_agency error:", e)
            fa_name = getattr(award.awarding_agency, "name", "Unknown Agency")
            fa_id = f"agency:{fa_name}"
            add_node(fa_id, "funding_agency", name=fa_name)
            # Program office node (if available)
            prog_office = getattr(award, "awarding_agency", None)
            if prog_office and getattr(prog_office, "subtier_agency", None):
                po_id = f"program:{prog_office.subtier_agency.abbreviation}"
                add_node(po_id, "program_office", name=prog_office.subtier_agency.name, parent=fa_id)
            else:
                po_id = fa_id
            # Prime contractor node
            if award.recipient:
                prime_id = f"prime:{award.recipient.duns or award.recipient.uei or award.recipient.name}"
                add_node(prime_id, "prime_contractor", name=award.recipient.name)
                # Edge: program office -> prime
                add_edge(po_id, prime_id, "prime_contract", value=award.total_obligation, award_id=award.award_identifier)
                # Subawards (suppliers)
                if getattr(award, "subaward_count", 0) > 0:
                    for subaward in award.subawards:
                        if subaward.recipient:
                            sub_id = f"supplier:{subaward.recipient.duns or subaward.recipient.uei or subaward.recipient.name}"
                            add_node(sub_id, "supplier", name=subaward.recipient.name)
                            add_edge(prime_id, sub_id, "subcontract", value=getattr(subaward, "amount", None), subaward_id=getattr(subaward, "subaward_number", None))

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

if __name__ == "__main__":
    extract_awards()
    # Output as JSON for next steps
    with open("usaspending_nodes.json", "w") as f:
        json.dump(list(g_nodes.values()), f, indent=2, default=decimal_default)
    with open("usaspending_edges.json", "w") as f:
        json.dump(g_edges, f, indent=2, default=decimal_default)
    print(f"Extracted {len(g_nodes)} nodes and {len(g_edges)} edges.")
